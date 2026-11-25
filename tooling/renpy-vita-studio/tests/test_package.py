from __future__ import annotations

import struct
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from renpy_vita_studio.package import build_vpk
from renpy_vita_studio.stage import StageError


def make_sfo() -> bytes:
    keys = b"TITLE_ID\x00"
    value = b"PCSE00001\x00"
    key_start = 20 + 16
    data_start = key_start + len(keys)
    entry = struct.pack("<HHIII", 0, 0x0204, len(value), len(value), 0)
    return struct.pack("<4sIIII", b"\x00PSF", 0x00000101, key_start, data_start, 1) + entry + keys + value


def make_staged_app(root: Path, with_eboot: bool = True) -> Path:
    app = root / "app" / "PCSE00001"
    (app / "sce_sys").mkdir(parents=True)
    (app / "sce_sys" / "param.sfo").write_bytes(make_sfo())
    (app / "sce_sys" / "icon0.png").write_bytes(b"png-placeholder")
    (app / "game").mkdir()
    (app / "game" / "script.rpy").write_text("label start:\n    return\n", encoding="utf-8")
    if with_eboot:
        (app / "eboot.bin").write_bytes(b"fake-self")
    return app


class VpkPackagingTests(unittest.TestCase):
    def test_invokes_vitasdk_and_verifies_archive_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = make_staged_app(root)
            output = root / "release" / "game.vpk"

            def fake_run(command, **kwargs):
                with zipfile.ZipFile(command[-1], "w") as archive:
                    archive.write(command[command.index("--eboot") + 1], "eboot.bin")
                    archive.write(command[command.index("--sfo") + 1], "sce_sys/param.sfo")
                    for index, value in enumerate(command):
                        if value == "--add":
                            source, destination = command[index + 1].split("=", 1)
                            source_path = Path(source)
                            if source_path.is_dir():
                                for child in source_path.rglob("*"):
                                    if child.is_file():
                                        archive.write(child, (Path(destination) / child.relative_to(source_path)).as_posix())
                            else:
                                archive.write(source, destination)
                return CompletedProcess(command, 0, "", "")

            with patch("renpy_vita_studio.package.shutil.which", return_value="/fake/vita-pack-vpk"), patch(
                "renpy_vita_studio.package.subprocess.run", side_effect=fake_run
            ) as run:
                result = build_vpk(app, output)

            self.assertTrue(output.is_file())
            self.assertEqual(result["title_id"], "PCSE00001")
            self.assertEqual(result["payload_files_added"], 2)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(
                    set(archive.namelist()),
                    {"eboot.bin", "sce_sys/param.sfo", "sce_sys/icon0.png", "game/script.rpy"},
                )
            self.assertFalse(run.call_args.kwargs["shell"])

    def test_requires_runtime_built_eboot(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = make_staged_app(Path(tmp), with_eboot=False)
            with self.assertRaisesRegex(StageError, "missing eboot.bin"):
                build_vpk(app, Path(tmp) / "out.vpk")

    def test_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = make_staged_app(root)
            output = root / "keep.vpk"
            output.write_bytes(b"keep")
            with self.assertRaisesRegex(StageError, "refusing to overwrite"):
                build_vpk(app, output)
            self.assertEqual(output.read_bytes(), b"keep")

    def test_requires_vpk_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = make_staged_app(root)
            with self.assertRaisesRegex(StageError, ".vpk extension"):
                build_vpk(app, root / "output.zip")

    def test_requires_vitasdk_packer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = make_staged_app(root)
            with patch("renpy_vita_studio.package.shutil.which", return_value=None):
                with self.assertRaisesRegex(StageError, "vita-pack-vpk was not found"):
                    build_vpk(app, root / "out.vpk")


if __name__ == "__main__":
    unittest.main()
