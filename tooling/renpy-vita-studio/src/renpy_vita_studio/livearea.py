"""Generate compact, Vita-oriented LiveArea artwork and SFO metadata."""
from __future__ import annotations
import re, struct
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont, ImageOps

class LiveAreaError(ValueError):
    pass

def _load_font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        try: return ImageFont.truetype(candidate, size)
        except OSError: pass
    return ImageFont.load_default()

def _source_image(source: Path | None, title: str) -> Image.Image:
    if source:
        try:
            with Image.open(source) as image:
                image.load()
                return ImageOps.exif_transpose(image).convert("RGB")
        except Exception as exc:
            raise LiveAreaError(f"Cannot open selected artwork {source}: {exc}") from exc
    image = Image.new("RGB", (1280, 720))
    draw = ImageDraw.Draw(image)
    for y in range(720):
        t=y/720
        draw.line((0,y,1280,y), fill=(int(18+22*t),int(25+18*t),int(48+42*t)))
    font=_load_font(64); label=title[:48]; box=draw.textbbox((0,0),label,font=font)
    draw.text(((1280-(box[2]-box[0]))/2,315),label,fill=(245,245,250),font=font)
    return image

def _save_fit(source: Image.Image, target: Path, size: tuple[int,int], max_bytes: int) -> None:
    target.parent.mkdir(parents=True,exist_ok=True)
    fitted=ImageOps.fit(source,size,method=Image.Resampling.LANCZOS,centering=(0.5,0.45))
    for colors in (256,128,64,32,16):
        indexed=fitted.quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
        indexed.save(target,format="PNG",optimize=True)
        if target.stat().st_size <= max_bytes: return
    raise LiveAreaError(f"Could not encode {target.name} below the Vita artwork limit of {max_bytes} bytes")

def generate_livearea(sce_sys: str | Path, title: str, artwork: str | Path | None = None) -> dict:
    root=Path(sce_sys); root.mkdir(parents=True,exist_ok=True)
    source_path=Path(artwork).expanduser().resolve() if artwork else None
    image=_source_image(source_path,title)
    targets={
        "icon0.png":((128,128),128*1024),
        "pic0.png":((960,544),256*1024),
        "livearea/contents/bg0.png":((840,500),128*1024),
        "livearea/contents/startup.png":((280,158),64*1024),
    }
    for relative,(size,limit) in targets.items(): _save_fit(image,root/relative,size,limit)
    template='''<?xml version="1.0" encoding="utf-8"?>
<livearea style="a1" format-ver="01.00" content-rev="1">
  <livearea-background>
    <image>bg0.png</image>
  </livearea-background>
  <gate>
    <startup-image>startup.png</startup-image>
  </gate>
</livearea>
'''
    contents=root/"livearea"/"contents"; contents.mkdir(parents=True,exist_ok=True)
    (contents/"template.xml").write_text(template,encoding="utf-8")
    return {"files":list(targets)+["livearea/contents/template.xml"],
            "dimensions":{k:list(v[0]) for k,v in targets.items()},
            "size_limits_bytes":{k:v[1] for k,v in targets.items()},
            "artwork_source":str(source_path) if source_path else "generated title card"}

def write_param_sfo(path: str | Path, title: str, title_id: str, app_version: str = "01.00") -> None:
    if not re.fullmatch(r"[A-Z]{4}[0-9]{5}",title_id):
        raise LiveAreaError("TITLE_ID must use the Vita format: 4 uppercase letters followed by 5 digits")
    fields=[("TITLE",title[:128].encode("utf-8")+b"\0"),("TITLE_ID",title_id.encode("ascii")+b"\0"),
            ("APP_VER",app_version.encode("ascii")+b"\0"),("CATEGORY",b"gd\0")]
    keys=bytearray(); data=bytearray(); entries=bytearray()
    for key,value in fields:
        ko=len(keys); keys.extend(key.encode("ascii")+b"\0")
        do=len(data); data.extend(value)
        entries.extend(struct.pack("<HHIII",ko,0x0204,len(value),len(value),do))
    key_start=20+len(entries); data_start=key_start+len(keys)
    header=struct.pack("<4sIIII",b"\0PSF",0x00000101,key_start,data_start,len(fields))
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(header+entries+keys+data)
