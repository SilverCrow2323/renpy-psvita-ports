from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw
from renpy_vita_studio.builder import build_game_vpk
from renpy_vita_studio.livearea import generate_livearea, write_param_sfo
from renpy_vita_studio.project_source import resolve_game_directory, default_title_id
from renpy_vita_studio.runtime_catalog import RUNTIMES
from renpy_vita_studio.runtime_manager import _safe_member, RuntimeError
from renpy_vita_studio.stage import _read_sfo

class GuidedBuilderTests(unittest.TestCase):
    def test_original_project_does_not_need_vita_scaffolding(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"My Game"; game=root/"game"; game.mkdir(parents=True)
            (game/"script.rpy").write_text("label start: pass",encoding="utf-8")
            (root/"sce_sys").mkdir(); (root/"eboot.bin").write_bytes(b"not used")
            resolved_root,resolved_game=resolve_game_directory(root)
            self.assertEqual(resolved_root,root.resolve()); self.assertEqual(resolved_game,game.resolve())
            self.assertRegex(default_title_id("My Game",root),r"^[A-Z]{4}[0-9]{5}$")

    def test_game_directory_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"project"; game=root/"game"; game.mkdir(parents=True)
            outside=Path(temp)/"outside.rpy"; outside.write_text("label start: pass",encoding="utf-8")
            (game/"linked.rpy").symlink_to(outside)
            with self.assertRaisesRegex(ValueError,"Symbolic links"): resolve_game_directory(root)

    def test_livearea_assets_and_param_sfo_are_generated(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"sce_sys"; artwork=Path(temp)/"cover.png"
            Image.new("RGB",(900,600),(30,80,120)).save(artwork)
            result=generate_livearea(root,"A <Test> Game",artwork)
            for relative, expected in (("icon0.png",(128,128)),("pic0.png",(960,544)),("livearea/contents/bg0.png",(840,500))):
                with Image.open(root/relative) as generated:
                    self.assertEqual(generated.size,expected)
            xml=(root/"livearea/contents/template.xml").read_text()
            self.assertIn("<image>bg0.png</image>",xml)
            write_param_sfo(root/"param.sfo","A Test Game","RNVX12345")
            _size,fields=_read_sfo(root/"param.sfo")
            self.assertEqual(fields["TITLE_ID"],"RNVX12345")
            self.assertEqual(fields["TITLE"],"A Test Game")
            write_param_sfo(root/"custom-id.sfo","Custom ID","RNPYHARVD")
            self.assertEqual(len(result["files"]),5)
            for relative,limit in result["size_limits_bytes"].items():
                self.assertLessEqual((root/relative).stat().st_size,limit)

    def test_runtime_catalogue_has_three_distinct_choices(self):
        self.assertEqual(set(RUNTIMES),{"renpy7-legacy","renpy8-pvr","renpy8-vgl"})
        self.assertIsNone(RUNTIMES["renpy7-legacy"]["sha256"])
        self.assertEqual(len(RUNTIMES["renpy8-pvr"]["sha256"]),64)
        self.assertIn("SHACCCG",RUNTIMES["renpy8-vgl"]["warning"].upper())

    def test_runtime_archive_path_traversal_is_rejected(self):
        with self.assertRaises(RuntimeError): _safe_member("../../outside.txt")
        with self.assertRaises(RuntimeError): _safe_member("C:/Windows/file.dll")

    def test_build_uses_only_original_game_directory_and_emits_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"OriginalGame"; game=root/"game"; game.mkdir(parents=True)
            (game/"script.rpy").write_text("label start: pass",encoding="utf-8")
            (root/"unneeded.txt").write_text("not copied",encoding="utf-8")
            runtime=Path(temp)/"runtime"; runtime.mkdir(); (runtime/"eboot.bin").write_bytes(b"fake-eboot")
            output=Path(temp)/"out"/"Game.vpk"
            def fake_pack(app,target):
                self.assertTrue((Path(app)/"game/script.rpy").is_file())
                self.assertTrue((Path(app)/"eboot.bin").is_file())
                self.assertFalse((Path(app)/"unneeded.txt").exists())
                self.assertTrue((Path(app)/"sce_sys/param.sfo").is_file())
                target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(b"fake-vpk")
                return {"output":str(target),"size_bytes":8,"entry_count":4}
            with patch("renpy_vita_studio.builder.ensure_runtime",return_value={"payload_path":str(runtime),"runtime_id":"test"}), patch("renpy_vita_studio.builder.build_vpk",side_effect=fake_pack):
                result=build_game_vpk(root,"renpy8-pvr","Game","RNVX12345",output)
            self.assertTrue(output.is_file()); self.assertTrue(Path(result["manifest"]).is_file())
            self.assertTrue(Path(result["checksum_file"]).is_file()); self.assertEqual(len(result["sha256"]),64)

if __name__=="__main__": unittest.main()
