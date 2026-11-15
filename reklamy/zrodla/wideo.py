"""Montaż reklam wideo Usnij: kadrowanie 4:5 i 9:16, polskie napisy z Pillow, plansza końcowa 2 s.

Napisy rysujemy w Pillow (PNG z przezroczystością) i nakładamy w ffmpeg, bo modele AI psują polskie znaki.
Gotowy plik przechodzi przez ffmpeg z -map_metadata -1 (bez metadanych).
"""
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

import usnij_grafika as g

TU = Path(__file__).resolve().parent
HF = TU / "hf"
WYJ = TU.parent
PACKSHOT = TU.parent.parent / "produkt" / "higgsfield" / "szara-packshot.jpg"
FPS = 30
FORMATY = {"4x5": (1080, 1350), "9x16": (1080, 1920)}
PLANSZA_S = 2.0
PRZEJSCIE_S = 0.35


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd))[:400] + "\n" + r.stderr[-2500:])
    return r


def dlugosc(plik):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(plik)])
    return float(json.loads(r.stdout)["format"]["duration"])


# ---------- napisy ----------

def napis_png(sciezka, w, h, linie, styl="naglowek", gora=None, tlo=True, dol=False):
    """Pełnoklatkowy PNG z napisem u góry kadru (albo nisko, gdy dol=True i podano gora)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pion = h > w * 1.4
    y0 = gora if gora is not None else (250 if pion else 70)
    if styl == "naglowek":
        f = g.font("serif", 78)
        odstep = 1.1
    elif styl == "maly":
        f = g.font("sans-semi", 44)
        odstep = 1.25
    else:  # duzy
        f = g.font("serif-bold", 96)
        odstep = 1.05
    wys = int(len(linie) * f.size * odstep)
    if tlo:
        # miękki ciemny „welon” pod tekstem
        warstwa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if dol:
            g.gradient(warstwa, h - 1, max(0, y0 - 260), alfa_od=215, alfa_do=0)
        else:
            g.gradient(warstwa, 0, min(h, y0 + wys + 220), alfa_od=200, alfa_do=0)
        img.alpha_composite(warstwa)
    g.tekst(img, (0, y0), linie, f, g.KREM, odstep=odstep, wyrownanie="srodek", szer=w)
    img.save(sciezka)
    return sciezka


def plansza_png(sciezka, w, h, packshot=PACKSHOT):
    g.plansza_koncowa(w, h, packshot).convert("RGB").save(sciezka)
    return sciezka


# ---------- montaż ----------

def kadr_filter(fmt, src_w, src_h, fokus_y=0.5, zoom=1.0):
    """Filtr ffmpeg: skaluje źródło (cover) i wycina kadr formatu, z punktem skupienia w pionie."""
    w, h = FORMATY[fmt]
    s = max(w / src_w, h / src_h) * zoom
    sw, sh = int(round(src_w * s / 2) * 2), int(round(src_h * s / 2) * 2)
    x = (sw - w) // 2
    y = int(min(max((sh - h) * fokus_y, 0), sh - h))
    return f"scale={sw}:{sh}:flags=lanczos,crop={w}:{h}:{x}:{y},setsar=1"


def wymiary(plik):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
             "-of", "json", str(plik)])
    s = json.loads(r.stdout)["streams"][0]
    return s["width"], s["height"]


def ujecie(src, fmt, wyj, start=0.0, dur=None, fokus_y=0.5, zoom=1.0, ken_burns=0.0, predkosc=1.0):
    """Jedno ujęcie: klip wideo albo zdjęcie (z delikatnym najazdem kamery), w formacie fmt, 30 fps."""
    w, h = FORMATY[fmt]
    src = Path(src)
    if src.suffix.lower() in (".png", ".jpg", ".jpeg"):
        sw, sh = Image.open(src).size
        n = int(round(dur * FPS))
        # duże skalowanie przed zoompan, żeby najazd był płynny
        s = max(w / sw, h / sh) * zoom * 2
        bw, bh = int(sw * s) // 2 * 2, int(sh * s) // 2 * 2
        x = (bw - 2 * w) // 2
        y = int(min(max((bh - 2 * h) * fokus_y, 0), bh - 2 * h))
        vf = (f"scale={bw}:{bh}:flags=lanczos,crop={2*w}:{2*h}:{x}:{y},"
              f"zoompan=z='1+{ken_burns}*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={w}x{h}:fps={FPS},"
              f"setsar=1,format=yuv420p")
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(src), "-vf", vf, "-frames:v", str(n),
             "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(wyj)])
    else:
        sw, sh = wymiary(src)
        vf = kadr_filter(fmt, sw, sh, fokus_y, zoom)
        if predkosc != 1.0:
            vf += f",setpts=PTS/{predkosc}"
        if ken_burns:
            vf += (f",scale={int(w*(1+ken_burns))//2*2}:-2,"
                   f"crop={w}:{h}:'(iw-{w})/2*t/{dur}':'(ih-{h})/2*t/{dur}'")
        vf += f",fps={FPS},format=yuv420p"
        cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(src)]
        if dur:
            cmd += ["-t", f"{dur / predkosc:.3f}"] if predkosc != 1.0 else ["-t", f"{dur:.3f}"]
        cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(wyj)]
        run(cmd)
    return wyj


def sklej(ujecia, wyj, przejscie=0.0):
    """Skleja ujęcia: twarde cięcia (przejscie=0) albo krótkie przenikania."""
    if przejscie <= 0:
        lst = Path(wyj).with_suffix(".txt")
        lst.write_text("".join(f"file '{Path(u).resolve()}'\n" for u in ujecia))
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-preset", "medium",
             "-crf", "16", "-r", str(FPS), "-pix_fmt", "yuv420p", "-an", str(wyj)])
        lst.unlink()
        return wyj
    wej, filt, prev, off = [], [], "[0:v]", 0.0
    for i, u in enumerate(ujecia):
        wej += ["-i", str(u)]
    for i in range(1, len(ujecia)):
        off += dlugosc(ujecia[i - 1]) - przejscie
        out = f"[x{i}]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={przejscie}:offset={off:.3f}{out}")
        prev = out
    run(["ffmpeg", "-y", *wej, "-filter_complex", ";".join(filt), "-map", prev, "-c:v", "libx264",
         "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-an", str(wyj)])
    return wyj


def z_napisami(wideo, napisy, wyj):
    """napisy: lista (png, od_s, do_s). Każdy napis wchodzi i schodzi miękko (0,25 s)."""
    wej = ["-i", str(wideo)]
    filt, prev = [], "[0:v]"
    for i, (png, od, do) in enumerate(napisy, start=1):
        wej += ["-loop", "1", "-t", f"{do + 0.5:.2f}", "-i", str(png)]
        filt.append(f"[{i}:v]format=rgba,fade=t=in:st={od:.2f}:d=0.25:alpha=1,"
                    f"fade=t=out:st={do - 0.25:.2f}:d=0.25:alpha=1[n{i}]")
        filt.append(f"{prev}[n{i}]overlay=0:0:enable='between(t,{od:.2f},{do:.2f})':shortest=0[v{i}]")
        prev = f"[v{i}]"
    run(["ffmpeg", "-y", *wej, "-filter_complex", ";".join(filt), "-map", prev, "-t", f"{dlugosc(wideo):.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-an", str(wyj)])
    return wyj


def z_plansza(wideo, plansza_jpg, wyj):
    """Dokleja 2 s planszy (marka + cena) z krótkim przenikaniem."""
    with tempfile.TemporaryDirectory() as t:
        pl = Path(t) / "pl.mp4"
        w, h = Image.open(plansza_jpg).size
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(plansza_jpg), "-t", f"{PLANSZA_S + PRZEJSCIE_S:.2f}",
             "-vf", f"scale={w}:{h},fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", "16", str(pl)])
        off = dlugosc(wideo) - PRZEJSCIE_S
        run(["ffmpeg", "-y", "-i", str(wideo), "-i", str(pl), "-filter_complex",
             f"[0:v][1:v]xfade=transition=fade:duration={PRZEJSCIE_S}:offset={off:.3f},format=yuv420p[v]",
             "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(wyj)])
    return wyj


def finalizuj(wideo, nazwa):
    """Ostatni przebieg: H.264, bez metadanych, szybki start w przeglądarce."""
    cel = WYJ / nazwa
    run(["ffmpeg", "-y", "-i", str(wideo), "-map", "0:v:0", "-map_metadata", "-1", "-map_chapters", "-1",
         "-fflags", "+bitexact", "-flags:v", "+bitexact", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-metadata:s:v:0", "encoder=", "-metadata:s:v:0", "handler_name=", "-an", str(cel)])
    return cel
