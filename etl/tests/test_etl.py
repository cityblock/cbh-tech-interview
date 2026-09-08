from pathlib import Path

import pytest

from etl.db import connect
from etl.extract import extract
from etl.pipeline import FIXTURES_DIR, ingest
from etl.transform import normalize_days, normalize_phone


@pytest.fixture
def db_file(tmp_path: Path) -> str:
    return str(tmp_path / "test.sqlite")


class TestTransform:
    def test_normalize_phone_accepts_common_formats(self) -> None:
        assert normalize_phone("(555) 555-0201") == "+15555550201"
        assert normalize_phone("555.555.0202") == "+15555550202"
        assert normalize_phone("+1 (555) 555-0205") == "+15555550205"
        assert normalize_phone("+15555550201") == "+15555550201"

    def test_normalize_phone_rejects_unparseable_input(self) -> None:
        assert normalize_phone("not-a-phone-number") is None

    def test_normalize_days_dedupes_and_orders_canonically(self) -> None:
        assert normalize_days(["Wed", "monday", "MON"]) == ["Mon", "Wed"]

    def test_normalize_days_rejects_unrecognized_day(self) -> None:
        assert normalize_days(["Monday", "Someday"]) is None

    def test_normalize_days_rejects_empty_input(self) -> None:
        assert normalize_days([]) is None


class TestExtract:
    def test_parses_csv_feed(self) -> None:
        records = extract(FIXTURES_DIR / "partner_a.csv")
        assert len(records) == 4
        marie = next(r for r in records if r.last_name == "Curie")
        assert marie.source == "partner_a"
        assert marie.phone_number == "(555) 555-0201"
        assert marie.availability_raw == ["Mon", "Wed", "Fri"]

    def test_parses_json_feed(self, tmp_path: Path) -> None:
        feed = tmp_path / "partner.json"
        feed.write_text(
            """[
  {
    "contact": { "first": "Chien-Shiung", "last": "Wu" },
    "phoneNumber": "+1 (555) 555-0205",
    "availableDays": ["Tuesday", "Thursday"]
  }
]"""
        )
        records = extract(feed)
        assert len(records) == 1
        wu = records[0]
        assert wu.source == "partner"
        assert wu.first_name == "Chien-Shiung"
        assert wu.availability_raw == ["Tuesday", "Thursday"]

    def test_parses_schedule_csv_feed(self) -> None:
        records = extract(FIXTURES_DIR / "partner_b.csv")
        assert len(records) == 9
        ada = next(r for r in records if r.last_name == "Lovelace")
        assert ada.source == "partner_b"
        assert ada.availability_raw == ["Monday", "Wednesday", "Friday"]
        assert '"schedule_windows"' in ada.raw_payload
        assert '"blocked_dates"' in ada.raw_payload

    def test_schedule_feed_rejects_rows_with_data_quality_issues(self, db_file: str) -> None:
        result = ingest([FIXTURES_DIR / "partner_b.csv"], db_file)
        assert result.staged == 9
        assert result.loaded == 5
        assert result.rejected == 4

    def test_raises_for_unregistered_extension(self, tmp_path: Path) -> None:
        unknown = tmp_path / "partner_b.xml"
        unknown.write_text("<rows />")
        with pytest.raises(ValueError, match="no parser registered"):
            extract(unknown)


class TestEnsureSchema:
    def test_records_users_migration_for_knex(self, db_file: str) -> None:
        connect(db_file)
        conn = connect(db_file)
        migration = conn.execute(
            "SELECT name FROM _migrations WHERE name = '0001_users'"
        ).fetchone()
        assert migration is not None


class TestIngestFixtures:
    def test_stages_every_row_regardless_of_validity(self, db_file: str) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv"], db_file)
        conn = connect(db_file)
        staged = conn.execute("SELECT COUNT(*) FROM raw_availability_events").fetchone()[0]
        assert staged == 4

    def test_loads_only_rows_that_pass_validation(self, db_file: str) -> None:
        result = ingest([FIXTURES_DIR / "partner_a.csv"], db_file)
        assert result.staged == 4
        assert result.rejected == 1
        assert result.loaded == 3

    def test_rejected_rows_never_reach_users(self, db_file: str) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv"], db_file)
        conn = connect(db_file)
        rejected = conn.execute(
            "SELECT first_name, last_name FROM raw_availability_events WHERE status = 'rejected'"
        ).fetchall()
        names = {(row["first_name"], row["last_name"]) for row in rejected}
        carson = conn.execute("SELECT id FROM users WHERE lastName = 'Carson'").fetchone()

        assert names == {(None, "Carson")}
        assert carson is None

    def test_rejection_errors_omit_phone_numbers(self, db_file: str) -> None:
        result = ingest([FIXTURES_DIR / "partner_b.csv"], db_file)
        conn = connect(db_file)
        rejected = conn.execute(
            "SELECT id, phone_number, error FROM raw_availability_events WHERE status = 'rejected'"
        ).fetchall()

        assert result.rejected == 4
        for row in rejected:
            assert row["phone_number"] not in (row["error"] or "")
            assert row["phone_number"] not in " ".join(result.errors)

    def test_rerunning_ingest_does_not_duplicate_users(self, db_file: str) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv"], db_file)
        ingest([FIXTURES_DIR / "partner_a.csv"], db_file)

        conn = connect(db_file)
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        staged_count = conn.execute("SELECT COUNT(*) FROM raw_availability_events").fetchone()[0]

        # The users table stays deduped on re-ingest, but the staging log
        # keeps every attempt — that's what makes it an audit trail.
        assert user_count == 3
        assert staged_count == 8
