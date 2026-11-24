from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from renpy_vita_studio.inspect import inspect_project


class ProjectInspectionTests(unittest.TestCase):
    def test_inventory_reports_archives_video_and_livearea_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / "game"
            game.mkdir()
            (game / "options.rpy").write_text('define config.name = "Example VN"\ndefine config.version = "1.2.3"\n', encoding="utf-8")
            (game / "archive.rpa").write_bytes(b"not parsed by inventory")
            (game / "opening.mp4").write_bytes(b"video")
            (game / "script.rpyc").write_bytes(b"compiled")
            (root / "sce_sys").mkdir()
            report = inspect_project(root)
            self.assertEqual(report["title"], "Example VN")
            self.assertEqual(report["game_version"], "1.2.3")
            self.assertEqual(report["file_count"], 4)
            self.assertEqual(report["rpa_archives"], ["game/archive.rpa"])
            self.assertEqual(report["video_files"], ["game/opening.mp4"])
            self.assertIn("video playback", " ".join(report["compatibility_hints"]).lower())
            self.assertFalse(report["vita_livearea"]["param_sfo"])

    def test_accepts_game_directory_as_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            game.mkdir()
            (game / "script.rpy").write_text("label start:\n    return\n", encoding="utf-8")
            report = inspect_project(game)
            self.assertEqual(report["game_directory"], str(game))


if __name__ == "__main__":
    unittest.main()
