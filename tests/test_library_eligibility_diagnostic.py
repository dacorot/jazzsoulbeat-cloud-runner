import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.library_eligibility_diagnostic import load_tracks, open_read_only_database


class ReadOnlyDatabaseTests(unittest.TestCase):
    def test_database_is_read_only_and_query_only(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "agent.db"
            connection = sqlite3.connect(db)
            connection.execute("CREATE TABLE tracks (file TEXT, approved INTEGER)")
            connection.execute("INSERT INTO tracks VALUES ('tracks/a.wav', 1)")
            connection.commit()
            connection.close()

            self.assertEqual(load_tracks(db)[0]["approved"], 1)
            read_only = open_read_only_database(db)
            try:
                self.assertEqual(read_only.execute("PRAGMA query_only").fetchone()[0], 1)
                with self.assertRaises(sqlite3.OperationalError):
                    read_only.execute("UPDATE tracks SET approved=0")
                with self.assertRaises(sqlite3.OperationalError):
                    read_only.execute("DELETE FROM tracks")
            finally:
                read_only.close()
            check = sqlite3.connect(db)
            try:
                self.assertEqual(check.execute("SELECT approved FROM tracks").fetchone()[0], 1)
            finally:
                check.close()


if __name__ == "__main__":
    unittest.main()
