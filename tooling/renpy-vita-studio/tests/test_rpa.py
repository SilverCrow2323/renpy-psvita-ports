from __future__ import annotations

import os
import pickle
import tempfile
import unittest
import zlib
from pathlib import Path

from renpy_vita_studio.rpa import RpaError, extract_rpa, inspect_rpa


def make_rpa(path: Path, entries, *, version="3", malicious=False):
    key = 0x42424242 if version == "3" else 0
    header_size = 34 if version == "3" else 24
    body = bytearray()
    index = {}
    for name, chunks in entries.items():
        records = []
        for payload, prefix in chunks:
            offset = header_size + len(body)
            body.extend(payload)
            if version == "3":
                records.append((offset ^ key, len(payload) ^ key, prefix))
            else:
                records.append((offset, len(payload)))
        index[name] = records
    index_offset = header_size + len(body)
    if malicious:
        index_bytes = zlib.compress(pickle.dumps(os.system, protocol=4))
    else:
        index_bytes = zlib.compress(pickle.dumps(index, protocol=4))
    if version == "3":
        header = f"RPA-3.0 {index_offset:016x} {key:08x}\n".encode("ascii")
    else:
        header = f"RPA-2.0 {index_offset:016x}".encode("ascii")
    path.write_bytes(header + body + index_bytes)
    return path


class RpaTests(unittest.TestCase):
    def test_rpa3_lists_and_extracts_fragmented_file_with_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = make_rpa(root / "game.rpa", {
                "story/line.txt": [(b"hello", b"PRE-"), (b"world", b"")],
                "images/bg.bin": [(b"\x00\x01", b"")],
            })
            archive = inspect_rpa(archive_path)
            self.assertEqual(archive.version, "RPA-3.0")
            self.assertEqual(archive.file_count, 2)
            destination = root / "extracted"
            written = extract_rpa(archive, destination)
            self.assertEqual(written, len(b"PRE-helloworld") + 2)
            self.assertEqual((destination / "story/line.txt").read_bytes(), b"PRE-helloworld")
            self.assertEqual((destination / "images/bg.bin").read_bytes(), b"\x00\x01")

    def test_rpa2_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = make_rpa(root / "old.rpa", {"game/script.rpyc": [(b"data", b"")]}, version="2")
            archive = inspect_rpa(archive_path)
            self.assertEqual(archive.version, "RPA-2.0")
            self.assertEqual(archive.total_size, 4)

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = make_rpa(Path(tmp) / "bad.rpa", {"../outside.txt": [(b"bad", b"")]})
            with self.assertRaisesRegex(RpaError, "path traversal"):
                inspect_rpa(archive_path)

    def test_rejects_pickle_globals(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = make_rpa(Path(tmp) / "evil.rpa", {}, malicious=True)
            with self.assertRaisesRegex(RpaError, "pickle global rejected"):
                inspect_rpa(archive_path)

    def test_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = inspect_rpa(make_rpa(root / "ok.rpa", {"a.txt": [(b"x", b"")]}))
            destination = root / "existing"
            destination.mkdir()
            with self.assertRaisesRegex(RpaError, "destination already exists"):
                extract_rpa(archive, destination)


if __name__ == "__main__":
    unittest.main()
