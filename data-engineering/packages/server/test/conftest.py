import os

# Must be set before server.db.engine is imported, since it reads DB_FILE at
# import time. Forced rather than defaulted so a test run can never write to the
# persisted development database.
os.environ["DB_FILE"] = ":memory:"
