"""Command-line interface for Ren'Py Vita Studio."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .inspect import inspect_project
from .doctor import inspect_environment
from .rpa import RpaError, extract_rpa, inspect_rpa
from .stage import StageError, stage_project
from .package import build_vpk


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="renpy-vita-studio",
        description="Inspect user-supplied Ren'Py projects and standard RPA archives safely.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="check host tools and VitaSDK availability (read-only)")

    stage = sub.add_parser("stage", help="prepare a non-destructive app/TITLE_ID staging folder")
    stage.add_argument("project", type=Path, help="project root containing game/ and sce_sys/")
    stage.add_argument("destination", type=Path, help="new output directory; existing app/TITLE_ID is never overwritten")
    stage.add_argument("--title-id", required=True, help="9-character Vita title ID, e.g. PCSE00001")

    package = sub.add_parser("vpk", help="package a staged app using VitaSDK's vita-pack-vpk")
    package.add_argument("staged_app", type=Path, help="app/TITLE_ID directory containing eboot.bin and sce_sys/")
    package.add_argument("output", type=Path, help="new .vpk output path; existing files are never overwritten")

    project = sub.add_parser("inspect", help="inventory a Ren'Py game project (read-only)")
    project.add_argument("path", type=Path)
    project.add_argument("--json", action="store_true", help="print the complete report as JSON")

    rpa = sub.add_parser("rpa", help="inspect or extract a standard RPA archive")
    rpa_sub = rpa.add_subparsers(dest="rpa_command", required=True)
    listing = rpa_sub.add_parser("list", help="list archive entries without extracting")
    listing.add_argument("archive", type=Path)
    listing.add_argument("--json", action="store_true")
    extraction = rpa_sub.add_parser("extract", help="extract into a new destination directory")
    extraction.add_argument("archive", type=Path)
    extraction.add_argument("destination", type=Path)
    extraction.add_argument("--max-total-gib", type=float, default=8.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            report = inspect_environment()
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0

        if args.command == "stage":
            report = stage_project(args.project, args.destination, args.title_id)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            print("Staging complete. This is not a VPK and has not been tested on a Vita.")
            return 0

        if args.command == "vpk":
            report = build_vpk(args.staged_app, args.output)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            print("VPK packaging complete. Installation and runtime have not been tested on a Vita.")
            return 0

        if args.command == "inspect":
            report = inspect_project(args.path)
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"Project: {report['title']}")
                print(f"Root: {report['project_root']}")
                print(f"Files: {report['file_count']} ({report['total_bytes']:,} bytes)")
                print(f"RPA archives: {len(report['rpa_archives'])}")
                print(f"Scripts: {report['script_files']} · video: {len(report['video_files'])} · native libraries: {len(report['native_libraries'])}")
                print("Hints:")
                for hint in report["compatibility_hints"]:
                    print(f"  - {hint}")
                print("This is an inventory report, not a compatibility verdict.")
            return 0

        archive = inspect_rpa(args.archive)
        if args.rpa_command == "list":
            records = [
                {"path": name, "chunks": len(chunks), "size": sum(len(c.prefix) + c.length for c in chunks)}
                for name, chunks in sorted(archive.entries.items())
            ]
            if args.json:
                print(json.dumps({"version": archive.version, "file_count": archive.file_count, "total_size": archive.total_size, "entries": records}, indent=2))
            else:
                print(f"{archive.path}: {archive.version} · {archive.file_count} files · {archive.total_size:,} bytes")
                for item in records:
                    print(f"{item['size']:>12,}  {item['path']}")
            return 0

        limit = int(args.max_total_gib * 1024**3)
        written = extract_rpa(archive, args.destination, max_total_bytes=limit)
        print(f"Extracted {archive.file_count} files ({written:,} bytes) to {args.destination}")
        return 0
    except (OSError, ValueError, RpaError, StageError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
