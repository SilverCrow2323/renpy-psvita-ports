#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(python3 -c 'import tomllib,sys; print(tomllib.load(open(sys.argv[1], "rb"))["project"]["version"])' "$ROOT/pyproject.toml")"
OUT="${1:-$ROOT/dist/renpy-vita-studio_${VERSION}_all.deb}"
OUT="$(mkdir -p "$(dirname "$OUT")" && cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PKG="$WORK/package"
install -d "$PKG/DEBIAN" "$PKG/usr/lib/renpy-vita-studio" "$PKG/usr/bin" "$PKG/usr/share/applications" "$PKG/usr/share/icons/hicolor/scalable/apps"
cp -a "$ROOT/src/renpy_vita_studio" "$PKG/usr/lib/renpy-vita-studio/"
cat > "$PKG/DEBIAN/control" <<CONTROL
Package: renpy-vita-studio
Version: $VERSION
Section: games
Priority: optional
Architecture: all
Maintainer: SPDW Factory
Depends: python3 (>= 3.11), python3-tk, python3-pil
Description: Guided Ren'Py Vita VPK builder
 Desktop application to inspect Ren'Py games, manage Vita runtimes,
 generate LiveArea assets and package PlayStation Vita VPK files.
CONTROL
cat > "$PKG/usr/bin/renpy-vita-studio-gui" <<'LAUNCH'
#!/bin/sh
export PYTHONPATH="/usr/lib/renpy-vita-studio${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m renpy_vita_studio.desktop "$@"
LAUNCH
cat > "$PKG/usr/bin/renpy-vita-studio" <<'LAUNCH'
#!/bin/sh
export PYTHONPATH="/usr/lib/renpy-vita-studio${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m renpy_vita_studio "$@"
LAUNCH
chmod 0755 "$PKG/usr/bin/renpy-vita-studio-gui" "$PKG/usr/bin/renpy-vita-studio"
install -m 0644 "$ROOT/packaging/linux/renpy-vita-studio.desktop" "$PKG/usr/share/applications/renpy-vita-studio.desktop"
install -m 0644 "$ROOT/packaging/linux/renpy-vita-studio.svg" "$PKG/usr/share/icons/hicolor/scalable/apps/renpy-vita-studio.svg"
dpkg-deb --build --root-owner-group "$PKG" "$OUT"
printf 'Built package: %s\n' "$OUT"
