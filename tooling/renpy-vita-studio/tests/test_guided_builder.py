from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from renpy_vita_studio.livearea import generate_livearea, write_param_sfo
from renpy_vita_studio.project_source import resolve_game_directory, discover_artwork, default_title_id
from renpy_vita_studio.runtime_catalog import RUNTIMES
from renpy_vita_studio.stage import _read_sfo


class GuidedBuilderTests(unittest.TestCase):
    def test_original_project_does_not_need_vita_scaffolding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "My Game"
            game = root / "game"
            game.mkdir(parents=True)
            (game / "script.rpy").write_text("label start: pass", encoding="utf-8")
            (root / "sce_sys").mkdir()
            (root / "eboot.bin").write_bytes(b"not used")
            resolved_root, resolved_game = resolve_game_directory(root)
            self.assertEqual(resolved_root, root)
            self.assertEqual(resolved_game, game)
            self.assertEqual(default_title_id("My Game", root).__len__(), 9)

    def test_game_directory_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            game = root / "game"
            game.mkdir(parents=True)
            outside = Path(temp) / "outside.rpy"
            outside.write_text("label start: pass", encoding="utf-8")
            (game / "linked.rpy").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "Symbolic links"):
                resolve_game_directory(root)

    def test_livearea_assets_and_param_sfo_are_generated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "sce_sys"
            artwork = Path(temp) / "cover.png"
            Image.new("RGB", (900, 600), (30, 80, 120)).save(artwork)
            result = generate_livearea(root, "A <Test> Game", artwork)
            self.assertEqual(Image.open(root / "icon0.png").size, (128, 128))
            self.assertEqual(Image.open(root / "pic0.png").size, (960, 544))
            self.assertTrue((root / "livearea/contents/template.xml").is_file())
            self.assertIn("A &lt;Test&gt; Game", (root / "livearea/contents/template.xml").read_text())
            write_param_sfo(root / "param.sfo", "A Test Game", "RNV123456")
            _size, fields = _read_sfo(root / "param.sfo")
            self.assertEqual(fields["TITLE_ID"], "RNV123456")
            self.assertEqual(fields["TITLE"], "A Test Game")
            self.assertEqual(len(result["files"]), 6)

    def test_runtime_catalogue_has_three_distinct_choices(self):
        self.assertEqual(set(RUNTIMES), {"renpy7-legacy", "renpy8-pvr", "renpy8-vgl"})
        self.assertIsNone(RUNTIMES["renpy7-legacy"]["sha256"])
        self.assertEqual(len(RUNTIMES["renpy8-pvr"]["sha256"]), 64)
        self.assertIn("SHACCCG", RUNTIMES["renpy8-vgl"]["warning"])

if __name__ == "__main__":
    unittest.main()
