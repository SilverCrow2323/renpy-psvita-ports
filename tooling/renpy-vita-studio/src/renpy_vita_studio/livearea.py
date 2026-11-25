"""Generate Vita LiveArea artwork and metadata from selected game artwork."""
from __future__ import annotations

import hashlib
import re
import struct
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont, ImageOps

class LiveAreaError(ValueError):
    pass

def _load_font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()

def _source_image(source: Path | None, title: str) -> Image.Image:
    if source:
        try:
            with Image.open(source) as image:
                image.load()
                return ImageOps.exif_transpose(image).convert("RGB")
        except Exception as exc:
            raise LiveAreaError(f"Cannot open selected artwork {source}: {exc}") from exc
    # A generated title card keeps the first build possible even when the game has no suitable image.
    image = Image.new("RGB", (1280, 720))
    draw = ImageDraw.Draw(image)
    for y in range(720):
        t = y / 720
        color = (int(18 + 22*t), int(25 + 18*t), int(48 + 42*t))
        draw.line((0, y, 1280, y), fill=color)
    font = _load_font(64)
    safe_title = title[:48]
    box = draw.textbbox((0, 0), safe_title, font=font)
    draw.text(((1280-(box[2]-box[0]))/2, 315), safe_title, fill=(245,245,250), font=font)
    return image

def _save_fit(source: Image.Image, target: Path, size: tuple[int, int]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fitted = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))
    fitted.save(target, format="PNG", optimize=True)

def generate_livearea(sce_sys: str | Path, title: str, artwork: str | Path | None = None) -> dict:
    root = Path(sce_sys)
    root.mkdir(parents=True, exist_ok=True)
    source_path = Path(artwork).expanduser().resolve() if artwork else None
    image = _source_image(source_path, title)
    targets = {
        "icon0.png": (128, 128),
        "pic0.png": (960, 544),
        "pic1.png": (280, 158),
        "livearea/contents/bg.png": (840, 500),
        "livearea/contents/startup.png": (280, 158),
    }
    for relative, size in targets.items():
        _save_fit(image, root / relative, size)

    safe_title = escape(title[:64])
    template = f'''<?xml version="1.0" encoding="utf-8"?>
<livearea style="a1" format="psmobile">
  <livearea-background>
    <image>bg.png</image>
  </livearea-background>
  <gate>
    <startup-image>startup.png</startup-image>
    <startup-text>{safe_title}</startup-text>
  </gate>
  <frame id="frame1">
    <image>bg.png</image>
  </frame>
  <text id="title">{safe_title}</text>
</livearea>
'''
    contents = root / "livearea" / "contents"
    contents.mkdir(parents=True, exist_ok=True)
    (contents / "template.xml").write_text(template, encoding="utf-8")
    return {"files": list(targets) + ["livearea/contents/template.xml"], "dimensions": {k: list(v) for k,v in targets.items()}, "artwork_source": str(source_path) if source_path else "generated title card"}

def _psf_string(key: str, value: str) -> tuple[str, bytes]:
    return key, value.encode("utf-8") + b"\0"

def write_param_sfo(path: str | Path, title: str, title_id: str, app_version: str = "01.00") -> None:
    if not re.fullmatch(r"[A-Z0-9]{9}", title_id):
        raise LiveAreaError("TITLE_ID must contain exactly 9 uppercase letters or digits")
    fields = [
        _psf_string("TITLE", title[:128]),
        _psf_string("TITLE_ID", title_id),
        _psf_string("APP_VER", app_version),
        _psf_string("CATEGORY", "gd"),
    ]
    key_table = bytearray()
    data_table = bytearray()
    entries = bytearray()
    for key, value in fields:
        key_offset = len(key_table)
        key_table.extend(key.encode("ascii") + b"\0")
        data_offset = len(data_table)
        data_table.extend(value)
        entries.extend(struct.pack("<HHIII", key_offset, 0x0204, len(value), len(value), data_offset))
    header_size = 20
    key_start = header_size + len(entries)
    data_start = key_start + len(key_table)
    header = struct.pack("<4sIIII", b"\0PSF", 0x00000101, key_start, data_start, len(fields))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(header + entries + key_table + data_table)
