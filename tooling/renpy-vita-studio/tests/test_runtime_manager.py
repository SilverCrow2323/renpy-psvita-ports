from __future__ import annotations

import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from renpy_vita_studio.runtime_manager import _download, RuntimeError
from renpy_vita_studio.runtime_catalog import RUNTIMES


class FakeResponse(io.BytesIO):
    def __init__(self, data: bytes, headers=None):
        super().__init__(data)
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class RuntimeDownloadTests(unittest.TestCase):
    def test_renpy8_runtime_digests_match_upstream_release_pins(self):
        self.assertEqual(
            RUNTIMES["renpy8-pvr"]["sha256"],
            "139a48dbcf7c8766a0ba7ada4e7db12a52d45b7600ce211f1b7c7ff15b16826e",
        )
        self.assertEqual(
            RUNTIMES["renpy8-vgl"]["sha256"],
            "742e9708c6132f76c93a0a96b9f894319709e5fa1bc01d2db1fd319ba41c6b76",
        )
        for runtime_id in ("renpy8-pvr", "renpy8-vgl"):
            self.assertRegex(RUNTIMES[runtime_id]["sha256"], r"^[0-9a-f]{64}$")

    def test_download_reports_progress_and_returns_sha256(self):
        data = b"x" * (5 * 1024 * 1024)
        progress = []
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "runtime.zip"
            response = FakeResponse(data, {"Content-Length": str(len(data))})
            with patch("renpy_vita_studio.runtime_manager.urllib.request.urlopen", return_value=response):
                digest = _download("https://example.invalid/runtime.zip", destination, progress.append)
            self.assertEqual(digest, hashlib.sha256(data).hexdigest())
            self.assertEqual(destination.read_bytes(), data)
            self.assertTrue(any("MiB" in message for message in progress))

    def test_oversized_content_length_is_rejected_before_download(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "runtime.zip"
            response = FakeResponse(b"", {"Content-Length": str(301 * 1024 * 1024)})
            with patch("renpy_vita_studio.runtime_manager.urllib.request.urlopen", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "300 MiB"):
                    _download("https://example.invalid/runtime.zip", destination)
            self.assertFalse(destination.exists())

    def test_empty_runtime_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "runtime.zip"
            with patch("renpy_vita_studio.runtime_manager.urllib.request.urlopen", return_value=FakeResponse(b"")):
                with self.assertRaisesRegex(RuntimeError, "empty"):
                    _download("https://example.invalid/runtime.zip", destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
