"""Bounded, defensive reader for standard Ren'Py RPA-2.0 and RPA-3.0 archives.

The RPA index is a Python pickle. Pickle is executable input: this module uses a
restricted unpickler, strict structure validation and bounded decompression.
Unknown/custom/encrypted archive variants are rejected rather than guessed.
"""

from __future__ import annotations

import codecs
import io
import os
import pickle
import re
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO

MAX_COMPRESSED_INDEX = 64 * 1024 * 1024
MAX_DECOMPRESSED_INDEX = 128 * 1024 * 1024
MAX_ENTRIES = 250_000
DEFAULT_MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
_HEADER_V3 = re.compile(rb"^RPA-3\.0 ([0-9a-fA-F]{16}) ([0-9a-fA-F]{8})\n$")
_HEADER_V2 = re.compile(rb"^RPA-2\.0 ([0-9a-fA-F]{16})")


class RpaError(ValueError):
    """Raised when an archive is malformed, unsupported or unsafe."""


@dataclass(frozen=True)
class RpaChunk:
    offset: int
    length: int
    prefix: bytes = b""


@dataclass(frozen=True)
class RpaArchive:
    path: Path
    version: str
    index_offset: int
    key: int
    entries: dict[str, tuple[RpaChunk, ...]]

    @property
    def file_count(self) -> int:
        return len(self.entries)

    @property
    def total_size(self) -> int:
        return sum(sum(len(c.prefix) + c.length for c in chunks) for chunks in self.entries.values())


class _RestrictedUnpickler(pickle.Unpickler):
    """Allow only the harmless bytes decoder used by some protocol-2 indexes."""

    def find_class(self, module: str, name: str):
        if module == "_codecs" and name == "encode":
            return codecs.encode
        raise RpaError(f"pickle global rejected: {module}.{name}")


def _safe_unpickle(data: bytes):
    stream = io.BytesIO(data)
    try:
        value = _RestrictedUnpickler(stream, encoding="latin1", errors="strict").load()
    except RpaError:
        raise
    except Exception as exc:
        raise RpaError(f"invalid RPA index pickle: {exc}") from exc
    if stream.read(1):
        raise RpaError("trailing data after RPA index pickle")
    return value


def _safe_member_name(name: object) -> str:
    if not isinstance(name, str):
        raise RpaError("archive entry name is not text")
    if not name or "\x00" in name or "\\" in name:
        raise RpaError(f"unsafe archive path: {name!r}")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise RpaError(f"absolute archive path rejected: {name!r}")
    path = PurePosixPath(name)
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise RpaError(f"path traversal or empty component rejected: {name!r}")
    if path.is_absolute():
        raise RpaError(f"absolute archive path rejected: {name!r}")
    return path.as_posix()


def _read_index(stream: BinaryIO, file_size: int, index_offset: int) -> bytes:
    if index_offset < 24 or index_offset >= file_size:
        raise RpaError("index offset is outside the archive")
    compressed_size = file_size - index_offset
    if compressed_size <= 0 or compressed_size > MAX_COMPRESSED_INDEX:
        raise RpaError("compressed index exceeds the configured safety limit")
    stream.seek(index_offset)
    compressed = stream.read(compressed_size)
    if len(compressed) != compressed_size:
        raise RpaError("truncated compressed index")
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(compressed, MAX_DECOMPRESSED_INDEX + 1)
        if len(raw) > MAX_DECOMPRESSED_INDEX or decoder.unconsumed_tail:
            raise RpaError("decompressed index exceeds the configured safety limit")
        tail = decoder.flush()
        if len(raw) + len(tail) > MAX_DECOMPRESSED_INDEX:
            raise RpaError("decompressed index exceeds the configured safety limit")
        raw += tail
        if not decoder.eof or decoder.unused_data:
            raise RpaError("invalid or trailing data in compressed index")
        return raw
    except zlib.error as exc:
        raise RpaError(f"invalid compressed index: {exc}") from exc


def inspect_rpa(path: str | os.PathLike[str]) -> RpaArchive:
    archive_path = Path(path)
    if not archive_path.is_file():
        raise RpaError(f"archive does not exist: {archive_path}")
    file_size = archive_path.stat().st_size
    with archive_path.open("rb") as stream:
        header = stream.read(40)
        if header.startswith(b"RPA-3.0 "):
            match = _HEADER_V3.match(header[:34])
            if not match:
                raise RpaError("malformed RPA-3.0 header")
            index_offset = int(match.group(1), 16)
            key = int(match.group(2), 16)
            version, header_size = "RPA-3.0", 34
        elif header.startswith(b"RPA-2.0 "):
            match = _HEADER_V2.match(header[:24])
            if not match:
                raise RpaError("malformed RPA-2.0 header")
            index_offset = int(match.group(1), 16)
            key = 0
            version, header_size = "RPA-2.0", 24
        else:
            raise RpaError("unsupported archive signature (supported: RPA-2.0, RPA-3.0)")

        if index_offset < header_size or index_offset >= file_size:
            raise RpaError("index offset is outside the data region")
        index_data = _read_index(stream, file_size, index_offset)
        index = _safe_unpickle(index_data)
        if not isinstance(index, dict):
            raise RpaError("RPA index root must be a dictionary")
        if len(index) > MAX_ENTRIES:
            raise RpaError("archive contains too many entries")

        entries: dict[str, tuple[RpaChunk, ...]] = {}
        for raw_name, raw_chunks in index.items():
            name = _safe_member_name(raw_name)
            if name in entries:
                raise RpaError(f"duplicate normalized archive path: {name}")
            if not isinstance(raw_chunks, (list, tuple)) or not raw_chunks:
                raise RpaError(f"invalid chunk list for {name!r}")
            chunks: list[RpaChunk] = []
            for raw_chunk in raw_chunks:
                if not isinstance(raw_chunk, (list, tuple)) or len(raw_chunk) not in (2, 3):
                    raise RpaError(f"invalid chunk record for {name!r}")
                encoded_offset, encoded_length = raw_chunk[0], raw_chunk[1]
                if not isinstance(encoded_offset, int) or not isinstance(encoded_length, int):
                    raise RpaError(f"non-integer chunk bounds for {name!r}")
                offset, length = encoded_offset ^ key, encoded_length ^ key
                prefix = raw_chunk[2] if len(raw_chunk) == 3 else b""
                if not isinstance(prefix, bytes):
                    raise RpaError(f"invalid inline prefix for {name!r}")
                if offset < header_size or length < 0 or offset > index_offset or length > index_offset - offset:
                    raise RpaError(f"chunk bounds outside data region for {name!r}")
                chunks.append(RpaChunk(offset, length, prefix))
            entries[name] = tuple(chunks)

    result = RpaArchive(archive_path, version, index_offset, key, entries)
    if result.total_size > DEFAULT_MAX_TOTAL_BYTES:
        raise RpaError("archive announces more than the default 8 GiB extraction limit")
    return result


def extract_rpa(
    archive: RpaArchive,
    destination: str | os.PathLike[str],
    *,
    overwrite: bool = False,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> int:
    """Extract to a new directory atomically; never follows archive-created paths."""
    target = Path(destination).expanduser().absolute()
    if target.exists() and (not overwrite or not target.is_dir()):
        raise RpaError(f"destination already exists: {target}")
    if max_total_bytes <= 0:
        raise RpaError("max_total_bytes must be positive")
    if archive.total_size > max_total_bytes:
        raise RpaError("archive exceeds the requested extraction size limit")

    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and overwrite:
        # Replacing an existing directory is intentionally not recursive. The caller
        # must choose a fresh destination to avoid accidental data loss.
        raise RpaError("overwrite of an existing directory is not supported; choose a new destination")
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}.extract-", dir=parent))
    written = 0
    try:
        with archive.path.open("rb") as source:
            for member, chunks in archive.entries.items():
                relative = PurePosixPath(member)
                output = temporary.joinpath(*relative.parts)
                resolved = output.resolve()
                if not resolved.is_relative_to(temporary.resolve()):
                    raise RpaError(f"extraction path escapes destination: {member!r}")
                output.parent.mkdir(parents=True, exist_ok=True)
                if output.exists() or output.is_symlink():
                    raise RpaError(f"duplicate or unsafe output path: {member!r}")
                with output.open("xb") as sink:
                    for chunk in chunks:
                        sink.write(chunk.prefix)
                        source.seek(chunk.offset)
                        remaining = chunk.length
                        while remaining:
                            block = source.read(min(1024 * 1024, remaining))
                            if not block:
                                raise RpaError(f"truncated payload for {member!r}")
                            sink.write(block)
                            remaining -= len(block)
                        written += len(chunk.prefix) + chunk.length
        os.replace(temporary, target)
        return written
    except Exception:
        import shutil
        shutil.rmtree(temporary, ignore_errors=True)
        raise
