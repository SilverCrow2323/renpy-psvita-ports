from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

from renpy_vita_studio.stage import StageError, stage_project


def make_sfo(title_id: str = "PCSE00001", title: str = "Example Vita Game") -> bytes:
    keys = b"TITLE_ID\x00TITLE\x00"
    title_bytes = title.encode("utf-8") + b"\x00"
    id_bytes = title_id.encode("utf-8") + b"\x00"
    values = id_bytes + title_bytes
    key_start = 20 + 2 * 16
    data_start = key_start + len(keys)
    records = [
        struct.pack("<HHIII", 0, 0x0204, len(id_bytes), len(id_bytes), 0),
        struct.pack("<HHIII", len(b"TITLE_ID\x00"), 0x0204, len(title_bytes), len(title_bytes), len(id_bytes)),
    ]
    header = struct.pack("<4sIIII", b"\x00PSF", 0x00000101, key_start, data_start, 2)
    return header + b"".join(records) + keys + values


def write_png(path: Path, width: int = 128, height: int = 128) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


def make_project(root: Path) -> Path:
    project = root / "project"
    (project / "game").mkdir(parents=True)
    (project / "game" / "script.rpy").write_text("label start:\n    return\n", encoding="utf-8")
    sce_sys = project / "sce_sys"
    sce_sys.mkdir()
    (sce_sys / "param.sfo").write_bytes(make_sfo())
    write_png(sce_sys / "icon0.png")
    write_png(sce_sys / "pic0.png", 960, 544)
    return project


class StagingTests(unittest.TestCase):
    def test_stages_into_app_layout_and_writes_hash_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            result = stage_project(project, root / "out", "PCSE00001")
            app = root / "out" / "app" / "PCSE00001"
            self.assertTrue((app / "game" / "script.rpy").is_file())
            self.assertTrue((app / "sce_sys" / "param.sfo").is_file())
            manifest = json.loads((app / "spdw-stage-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["title_id"], "PCSE00001")
            self.assertEqual(manifest["vita_metadata"]["icon0_png_dimensions"], [128, 128])
            self.assertEqual(manifest["vita_metadata"]["param_sfo_fields"]["TITLE_ID"], "PCSE00001")
            self.assertEqual(result["file_count"], 4)
            self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["files"]))
            self.assertTrue((project / "game" / "script.rpy").is_file())

    def test_rejects_invalid_title_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            with self.assertRaisesRegex(StageError, "9 uppercase"):
                stage_project(project, root / "out", "bad-id")

    def test_refuses_existing_destination_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            app = root / "out" / "app" / "PCSE00001"
            app.mkdir(parents=True)
            sentinel = app / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(StageError, "refusing to overwrite"):
                stage_project(project, root / "out", "PCSE00001")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_rejects_invalid_sfo_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            (project / "sce_sys" / "param.sfo").write_bytes(b"not-a-psf-file" + b"\\x00" * 20)
            with self.assertRaisesRegex(StageError, "PSF magic"):
                stage_project(project, root / "out", "PCSE00001")

    def test_rejects_title_id_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            (project / "sce_sys" / "param.sfo").write_bytes(make_sfo("PCSE99999"))
            with self.assertRaisesRegex(StageError, "title ID mismatch"):
                stage_project(project, root / "out", "PCSE00001")

    def test_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = make_project(root)
            target = root / "outside.txt"
            target.write_text("outside", encoding="utf-8")
            try:
                (project / "game" / "linked.txt").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this runner")
            with self.assertRaisesRegex(StageError, "symbolic links"):
                stage_project(project, root / "out", "PCSE00001")


if __name__ == "__main__":
    unittest.main()
