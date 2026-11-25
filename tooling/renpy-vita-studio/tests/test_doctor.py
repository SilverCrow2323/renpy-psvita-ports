from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from renpy_vita_studio.doctor import inspect_environment


class EnvironmentDoctorTests(unittest.TestCase):
    def test_reports_missing_sdk_without_claiming_readiness(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "renpy_vita_studio.doctor.shutil.which", return_value=None
        ):
            report = inspect_environment()
        self.assertEqual(report["vita_sdk"]["status"], "not-detected")
        self.assertFalse(report["tools"]["vita_cc"]["available"])
        self.assertTrue(any("does not run compilers" in note for note in report["notes"]))

    def test_reports_core_toolchain_components_without_claiming_full_readiness(self):
        required = {"arm-vita-eabi-gcc", "arm-vita-eabi-g++", "vita-pack-vpk", "vita-mksfoex", "cmake", "make"}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"VITASDK": tmp}, clear=True
        ), patch(
            "renpy_vita_studio.doctor.shutil.which",
            side_effect=lambda name: f"/fake/{name}" if name in required else None,
        ):
            Path(tmp, "bin").mkdir()
            report = inspect_environment()
        self.assertEqual(report["vita_sdk"]["status"], "core-tools-detected")
        self.assertTrue(report["tools"]["vita_pack_vpk"]["available"])
        self.assertTrue(any("do not prove" in note for note in report["notes"]))

    def test_reports_partial_sdk_configuration(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"VITASDK": tmp}, clear=True
        ), patch("renpy_vita_studio.doctor.shutil.which", return_value=None):
            report = inspect_environment()
        self.assertEqual(report["vita_sdk"]["status"], "partial")
        self.assertTrue(report["vita_sdk"]["path_exists"])


if __name__ == "__main__":
    unittest.main()
