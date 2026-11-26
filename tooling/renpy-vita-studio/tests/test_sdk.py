from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from renpy_vita_studio.sdk import configure_vitasdk_path


class VitaSDKDiscoveryTests(unittest.TestCase):
    def test_missing_home_directory_is_not_fatal(self):
        with patch.dict(os.environ, {"PATH": ""}, clear=True), patch(
            "renpy_vita_studio.sdk.Path.home",
            side_effect=RuntimeError("Could not determine home directory"),
        ), patch("renpy_vita_studio.sdk.Path.is_dir", return_value=False):
            self.assertIsNone(configure_vitasdk_path())

    def test_configured_sdk_bin_is_added_to_process_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sdk_root = Path(tmp)
            bindir = sdk_root / "bin"
            bindir.mkdir()
            with patch.dict(
                os.environ,
                {"VITASDK": str(sdk_root), "PATH": ""},
                clear=True,
            ), patch(
                "renpy_vita_studio.sdk.Path.home",
                side_effect=RuntimeError("home unavailable"),
            ):
                self.assertEqual(configure_vitasdk_path(), str(sdk_root.resolve()))
                self.assertIn(str(bindir.resolve()), os.environ["PATH"].split(os.pathsep))


if __name__ == "__main__":
    unittest.main()
