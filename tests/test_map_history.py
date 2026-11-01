import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from control_screen import ControlScreen


class MapHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cwd = Path.cwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.temp_dir.cleanup()

    def test_missing_settings_file_starts_with_empty_history(self):
        self.assertEqual(ControlScreen._load_history(None), {})

    def test_invalid_json_starts_with_empty_history(self):
        Path("map_settings.json").write_text("{not valid json", encoding="utf-8")

        self.assertEqual(ControlScreen._load_history(None), {})

    def test_loads_existing_history(self):
        history = {
            "/maps/forest.png": {
                "pos": [12.5, -8.0],
                "zoom_factor": 1.25,
                "rotation": 90,
            }
        }
        Path("map_settings.json").write_text(json.dumps(history), encoding="utf-8")

        self.assertEqual(ControlScreen._load_history(None), history)

    def test_saves_history_as_json(self):
        history = {"/maps/cave.svg": {"pos": [0, 0], "zoom_factor": 2.0, "rotation": 180}}
        screen = SimpleNamespace(map_history=history)

        ControlScreen._save_history(screen)

        self.assertEqual(json.loads(Path("map_settings.json").read_text(encoding="utf-8")), history)


if __name__ == "__main__":
    unittest.main()
