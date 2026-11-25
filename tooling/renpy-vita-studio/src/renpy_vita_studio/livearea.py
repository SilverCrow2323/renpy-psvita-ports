"""Generate compact, Vita-oriented LiveArea artwork and SFO metadata."""
from __future__ import annotations
import re,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

class LiveAreaError(ValueError): pass

def _load_font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        try: return ImageFont.truetype(candidate,size)
        except OSError: pass
    return ImageFont.load_default()

def _source_image(source: Path | None,title: str,preserve_alpha: bool=False) -> Image.Image:
    if source:
        try:
            with Image.open(source) as image:
                image.load()
                normalized=ImageOps.exif_transpose(image)
                if preserve_alpha and ("A" in normalized.getbands() or "transparency" in normalized.info):
                    return normalized.convert("RGBA")
                return normalized.convert("RGB")
        except Exception as exc:
            raise LiveAreaError(f"Cannot open selected artwork {source}: {exc}") from exc
    image=Image.new("RGB",(1280,720)); draw=ImageDraw.Draw(image)
    for y in range(720):
        t=y/720
        draw.line((0,y,1280,y),fill=(int(18+22*t),int(25+18*t),int(48+42*t)))
    font=_load_font(64); label=title[:48]; box=draw.textbbox((0,0),label,font=font)
    draw.text(((1280-(box[2]-box[0]))/2,315),label,fill=(245,245,250),font=font)
    return image

def _save_fit(source: Image.Image,target: Path,size: tuple[int,int],max_bytes: int,preserve_alpha: bool=False) -> None:
    target.parent.mkdir(parents=True,exist_ok=True)
    fitted=ImageOps.fit(source,size,method=Image.Resampling.LANCZOS,centering=(0.5,0.45))
    alpha=preserve_alpha and fitted.mode=="RGBA"
    for colors in (256,128,64,32,16):
        if alpha:
            indexed=fitted.quantize(colors=colors,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
        else:
            indexed=fitted.convert("RGB").quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
        indexed.save(target,format="PNG",optimize=True)
        if target.stat().st_size<=max_bytes: return
    raise LiveAreaError(f"Could not encode {target.name} below the Vita artwork limit of {max_bytes} bytes")

def generate_livearea(sce_sys: str | Path,title: str,artwork=None) -> dict:
    root=Path(sce_sys); root.mkdir(parents=True,exist_ok=True)
    if isinstance(artwork,dict):
        sources={key:(Path(value).expanduser().resolve() if value else None) for key,value in artwork.items()}
    elif artwork:
        shared=Path(artwork).expanduser().resolve()
        sources={key:shared for key in ("icon0","pic0","bg0","startup")}
    else: sources={}
    targets={
        "icon0.png":("icon0",(128,128),128*1024,False),
        "pic0.png":("pic0",(960,544),256*1024,False),
        "livearea/contents/bg0.png":("bg0",(840,500),128*1024,False),
        "livearea/contents/startup.png":("startup",(280,158),64*1024,True),
    }
    source_report={}
    for relative,(key,size,limit,alpha) in targets.items():
        source=sources.get(key)
        _save_fit(_source_image(source,title,preserve_alpha=alpha),root/relative,size,limit,preserve_alpha=alpha)
        source_report[key]=str(source) if source else "generated title card"
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
    (contents/"template.xml").write_bytes(template.replace("\n","\r\n").encode("utf-8"))
    return {"files":list(targets)+["livearea/contents/template.xml"],
            "dimensions":{relative:list(data[1]) for relative,data in targets.items()},
            "size_limits_bytes":{relative:data[2] for relative,data in targets.items()},
            "artwork_sources":source_report}

def _utf8_value(value: str,max_bytes: int) -> bytes:
    return value.encode("utf-8")[:max_bytes].decode("utf-8","ignore").encode("utf-8")+b"\0"

def write_param_sfo(path: str | Path,title: str,title_id: str,app_version: str="01.00") -> None:
    if not re.fullmatch(r"[A-Z0-9]{9}",title_id):
        raise LiveAreaError("TITLE_ID must contain exactly 9 uppercase letters or digits")
    if not re.fullmatch(r"\d{2}\.\d{2}",app_version):
        raise LiveAreaError("App version must use the XX.XX format, for example 01.00")
    fields=[("TITLE",_utf8_value(title,128)),("TITLE_ID",title_id.encode("ascii")+b"\0"),
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
