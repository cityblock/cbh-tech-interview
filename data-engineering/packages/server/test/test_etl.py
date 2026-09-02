from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import func, select

from server.db.engine import Session, engine
from server.db.migrate import migrate
from server.db.models import RawAvailabilityEvent, User
from server.etl.extract import extract
from server.etl.pipeline import FIXTURES_DIR, ingest
from server.etl.transform import normalize_days, normalize_phone


# Function-scoped (unlike test_user.py's module-scoped fixture) so every test
# starts from an empty database — several tests below assert exact row
# counts after one or two `ingest()` calls, which only holds if no other
# test's rows are still sitting in the same in-memory database.
@pytest.fixture(autouse=True)
def migrated() -> Iterator[None]:
    migrate()
    yield
    engine.dispose()


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

    def test_parses_json_feed(self) -> None:
        records = extract(FIXTURES_DIR / "partner_b.json")
        assert len(records) == 4
        wu = next(r for r in records if r.last_name == "Wu")
        assert wu.source == "partner_b"
        assert wu.first_name == "Chien-Shiung"
        assert wu.availability_raw == ["Tuesday", "Thursday"]

    def test_raises_for_unregistered_extension(self, tmp_path: Path) -> None:
        unknown = tmp_path / "partner_c.xml"
        unknown.write_text("<rows />")
        with pytest.raises(ValueError, match="no parser registered"):
            extract(unknown)


class TestIngestFixtures:
    def test_stages_every_row_regardless_of_validity(self) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])
        with Session() as db:
            staged = db.scalar(select(func.count()).select_from(RawAvailabilityEvent))
        assert staged == 8

    def test_loads_only_rows_that_pass_validation(self) -> None:
        result = ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])
        assert result.staged == 8
        # Carson (missing name), Carson (bad day), Lamarr (bad phone).
        assert result.rejected == 3
        assert result.loaded == 5

    def test_merges_duplicate_person_across_sources_by_phone(self) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])
        with Session() as db:
            matches = db.scalars(select(User).where(User.phoneNumber == "+15555550201")).all()

        assert len(matches) == 1
        # partner_b is ingested after partner_a and adds Saturday, so its
        # version of Marie Curie's availability is the one that survives.
        assert matches[0].availability == '{"availableDays":["Mon","Wed","Fri","Sat"]}'

    def test_rejected_rows_never_reach_users(self) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])
        with Session() as db:
            rejected = db.scalars(
                select(RawAvailabilityEvent).where(RawAvailabilityEvent.status == "rejected")
            ).all()
            names = {(e.first_name, e.last_name) for e in rejected}
            carson = db.scalar(select(User).where(User.lastName == "Carson"))
            lamarr = db.scalar(select(User).where(User.lastName == "Lamarr"))

        assert names == {(None, "Carson"), ("Rachel", "Carson"), ("Hedy", "Lamarr")}
        assert carson is None
        assert lamarr is None

    def test_rerunning_ingest_does_not_duplicate_users(self) -> None:
        ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])
        ingest([FIXTURES_DIR / "partner_a.csv", FIXTURES_DIR / "partner_b.json"])

        with Session() as db:
            user_count = db.scalar(select(func.count()).select_from(User))
            staged_count = db.scalar(select(func.count()).select_from(RawAvailabilityEvent))

        # The users table stays deduped on re-ingest, but the staging log
        # keeps every attempt — that's what makes it an audit trail.
        assert user_count == 4
        assert staged_count == 16
