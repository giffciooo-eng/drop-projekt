"""Reklamy 3 i 4 (wideo AI z Higgsfield) w formatach 4:5 i 9:16, z napisami i planszą końcową."""
import tempfile
from pathlib import Path

import wideo as v

HF = v.HF

# (linie, od_s, do_s); pozycja napisów: "gora" albo "dol" (nisko, nad kołdrą)
REKLAMY = {
    3: {
        "zrodlo": HF / "r3-wideo.mp4",
        "pozycja": "gora",
        "napisy": [
            (["240 g spokoju", "na powiekach"], 0.0, 2.3),
            (["Szklane kulki", "w miękkim polarze"], 2.45, 4.25),
            (["Ciemno. Cicho.", "Spokojnie."], 4.4, 6.0),
        ],
    },
    4: {
        "zrodlo": HF / "r4-wideo.mp4",
        "pozycja": "dol",
        "fokus_4x5": 0.12,   # w 4:5 kadr wyżej, żeby było widać partnera z lampką
        "packshot": v.PACKSHOT.with_name("czarna-packshot.jpg"),
        "napisy": [
            (["3:07. Znowu nie śpisz,", "a obok świeci lampka?"], 0.0, 2.5),
            (["Połóż maskę na oczach."], 2.65, 4.7),
            (["Ciemno. Cicho.", "Spokojnie."], 4.85, 7.0),
        ],
    },
}


def zbuduj(nr, fmt):
    cfg = REKLAMY[nr]
    w, h = v.FORMATY[fmt]
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        fokus = cfg.get("fokus_4x5", 0.5) if fmt == "4x5" else 0.5
        baza = v.ujecie(cfg["zrodlo"], fmt, t / "baza.mp4", fokus_y=fokus)
        napisy = []
        for i, (linie, od, do) in enumerate(cfg["napisy"]):
            if cfg["pozycja"] == "dol":
                y = (1180 if fmt == "9x16" else 1000) - (len(linie) - 1) * 40
                png = v.napis_png(t / f"n{i}.png", w, h, linie, gora=y, dol=True)
            else:
                png = v.napis_png(t / f"n{i}.png", w, h, linie)
            napisy.append((png, od, do))
        z_nap = v.z_napisami(baza, napisy, t / "napisy.mp4")
        pl = v.plansza_png(t / "plansza.jpg", w, h, cfg.get("packshot", v.PACKSHOT))
        cale = v.z_plansza(z_nap, pl, t / "cale.mp4")
        return v.finalizuj(cale, f"reklama-{nr}-{fmt}.mp4")


if __name__ == "__main__":
    for nr in (3, 4):
        for fmt in ("4x5", "9x16"):
            print(zbuduj(nr, fmt), round(v.dlugosc(v.WYJ / f"reklama-{nr}-{fmt}.mp4"), 2), "s")
