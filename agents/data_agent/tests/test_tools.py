import tempfile
import unittest
from pathlib import Path
from data_agent.tools import build_catalog, count_recordings, list_recordings, latest_recording


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "catalog.sqlite"
        source = Path(__file__).parents[1] / "sample_data" / "recordings.csv"
        self.assertEqual(build_catalog(source, self.db), 3)

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_original_sources(self):
        self.assertEqual(count_recordings(self.db), 3)
        self.assertEqual(count_recordings(self.db, direction="anticlockwise"), 2)
        self.assertEqual(count_recordings(self.db, direction="anticlockwise", validity="validated"), 1)

    def test_rejects_invalid_filter(self):
        with self.assertRaises(ValueError):
            count_recordings(self.db, sqlite="DROP TABLE")
        with self.assertRaises(ValueError):
            count_recordings(self.db, direction="sideways")

    def test_listing_and_latest(self):
        rows = list_recordings(self.db, limit=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(latest_recording(self.db)["recording_id"], "mock-003")

    def test_rejects_duplicate_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.csv"
            sample = (Path(__file__).parents[1] / "sample_data" / "recordings.csv").read_text()
            p.write_text(sample + sample.splitlines()[1] + "\n")
            with self.assertRaises(ValueError):
                build_catalog(p, Path(tmp) / "bad.sqlite")


if __name__ == "__main__":
    unittest.main()
