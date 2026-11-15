"""Reklamy 5 i 6 (montaże) w formatach 4:5 i 9:16, z polskimi napisami i planszą końcową.

Ujęcia wybrane ze stykówki (reklamy/stykowka-montaze.jpg):
- reklama 5 (od rozpakowania do efektu): K1 → K2 → K3 (maska opada) → K3 (gaśnie lampka)
- reklama 6 (hak tekstowy + zbliżenia): Z6 → Z3 → Z4 → Z5 → K6 (przepinanie z tyłu) → K3 (maska na oczach)
"""
import sys
import tempfile
from pathlib import Path

import wideo as v

HF = v.HF
P = v.PACKSHOT.parent          # produkt/higgsfield
PRZEJSCIE = 0.15

# ujęcie: (plik, opcje dla v.ujecie, napis albo None)
MONTAZE = {
    5: [
        (HF / "m-rozpakowanie.mp4", dict(start=0.2, dur=4.6, predkosc=1.85), ["Rozpakuj."]),
        (HF / "m-wyjmowanie.mp4", dict(start=0.3, dur=3.6, predkosc=1.8), ["Poczuj ciężar", "w dłoni."]),
        (HF / "r3-wideo.mp4", dict(start=0.0, dur=2.0), ["Połóż na oczach."]),
        (HF / "r3-wideo.mp4", dict(start=4.5, dur=1.5), ["Zgaś światło."]),
    ],
    6: [
        (HF / "r6-makro.jpg", dict(dur=1.7, ken_burns=0.07), ["Twoja maska się zsuwa", "i przepuszcza światło?"]),
        (P / "szara-makro-srodek.jpg", dict(dur=1.3, ken_burns=0.06), ["4 komory", "ze szklanymi kulkami"]),
        (P / "szara-makro-polar.jpg", dict(dur=1.3, ken_burns=0.06, fokus_x=0.62), ["Miękki,", "podwójny polar"]),
        (P / "szara-makro-koniec.jpg", dict(dur=1.3, ken_burns=0.06), ["Końce", "bez wypełnienia"]),
        (HF / "m-przepinanie.mp4", dict(start=1.1, dur=3.9, predkosc=2.4), ["Albo przepnij z tyłu.", "Bez gumki."]),
        (HF / "r3-wideo.mp4", dict(start=3.0, dur=1.4), ["Ciemno. Cicho.", "Spokojnie."]),
    ],
}


def zbuduj(nr, fmt):
    w, h = v.FORMATY[fmt]
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        uj, napisy, czas = [], [], 0.0
        for i, (plik, opcje, linie) in enumerate(MONTAZE[nr]):
            u = v.ujecie(plik, fmt, t / f"u{i}.mp4", **opcje)
            d = v.dlugosc(u)
            uj.append(u)
            if linie:
                od = 0.0 if i == 0 else czas + 0.05
                napisy.append((v.napis_png(t / f"n{i}.png", w, h, linie), od, czas + d - PRZEJSCIE))
            czas += d - PRZEJSCIE
        film = v.sklej(uj, t / "film.mp4", przejscie=PRZEJSCIE)
        z_nap = v.z_napisami(film, napisy, t / "napisy.mp4")
        pl = v.plansza_png(t / "plansza.jpg", w, h)
        cale = v.z_plansza(z_nap, pl, t / "cale.mp4")
        return v.finalizuj(cale, f"reklama-{nr}-{fmt}.mp4")


if __name__ == "__main__":
    numery = [int(a) for a in sys.argv[1:]] or [5, 6]
    for nr in numery:
        for fmt in ("4x5", "9x16"):
            print(zbuduj(nr, fmt), round(v.dlugosc(v.WYJ / f"reklama-{nr}-{fmt}.mp4"), 2), "s")
