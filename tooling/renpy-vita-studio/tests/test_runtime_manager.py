from __future__ import annotations

import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from renpy_vita_studio.runtime_manager import _download, RuntimeError


class FakeResponse(io.BytesIO):
    def __init__(self, data: bytes, headers=None):
        super().__init__(data)
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class RuntimeDownloadTests(unittest.TestCase):
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
