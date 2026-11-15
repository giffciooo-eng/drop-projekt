"""Kontrola gotowych reklam: komplet plików, wymiary, długość wideo (5–10 s), metadane."""
import json
import subprocess
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parent.parent
WYM = {"4x5": (1080, 1350), "9x16": (1080, 1920)}
ok = True


def blad(msg):
    global ok
    ok = False
    print("  BŁĄD:", msg)


for nr in range(1, 7):
    for fmt, (w, h) in WYM.items():
        ext = "jpg" if nr <= 2 else "mp4"
        f = R / f"reklama-{nr}-{fmt}.{ext}"
        if not f.exists():
            blad(f"brak pliku {f.name}")
            continue
        if ext == "jpg":
            im = Image.open(f)
            meta = {k: v for k, v in im.info.items() if k not in ("jfif", "jfif_version", "jfif_unit", "jfif_density", "progressive", "progression")}
            exif = bool(im.getexif())
            print(f"{f.name}: {im.size}, EXIF: {'tak' if exif else 'nie'}, inne metadane: {meta or 'brak'}")
            if im.size != (w, h):
                blad("zły rozmiar")
            if exif or meta:
                blad("metadane w obrazie")
        else:
            p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                           "stream=codec_type,width,height:format=duration:format_tags",
                                           "-of", "json", str(f)], capture_output=True, text=True).stdout)
            v = [s for s in p["streams"] if s["codec_type"] == "video"][0]
            dur = float(p["format"]["duration"])
            tagi = p["format"].get("tags", {})
            dziwne = {k: x for k, x in tagi.items() if k not in ("major_brand", "minor_version", "compatible_brands")}
            audio = any(s["codec_type"] == "audio" for s in p["streams"])
            print(f"{f.name}: {v['width']}x{v['height']}, {dur:.2f} s, dźwięk: {'tak' if audio else 'nie'}, "
                  f"tagi poza standardem MP4: {dziwne or 'brak'}")
            if (v["width"], v["height"]) != (w, h):
                blad("zły rozmiar")
            if not 5 <= dur <= 10.05:
                blad("długość poza 5–10 s")
            if dziwne:
                blad("metadane w wideo")

print("\nWYNIK:", "wszystko OK" if ok else "są błędy")
