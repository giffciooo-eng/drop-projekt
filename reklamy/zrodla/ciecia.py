"""Wykrywa cięcia i przeskoki w klipie: nagłą zmianę obrazu między sąsiednimi klatkami.

Użycie: python3 ciecia.py plik.mp4 [plik2.mp4 ...]
Przeskok = różnica klatek dużo większa niż typowa dla płynnego ruchu w tym klipie.
"""
import subprocess
import sys

import numpy as np


def skanuj(plik, w=108, h=192):
    fps_txt = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=r_frame_rate", "-of", "csv=p=0", plik], capture_output=True, text=True).stdout
    a, b = fps_txt.strip().split("/")
    fps = float(a) / float(b)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", plik, "-vf", f"scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
    d = np.abs(np.diff(f, axis=0)).mean((1, 2))
    med = float(np.median(d))
    prog = max(6.0, med * 5)
    skoki = [((i + 1) / fps, float(d[i])) for i in range(len(d)) if d[i] > prog]
    return med, prog, skoki


if __name__ == "__main__":
    for plik in sys.argv[1:]:
        med, prog, skoki = skanuj(plik)
        opis = ", ".join(f"{t:.2f} s ({v:.1f})" for t, v in skoki) or "brak"
        print(f"{plik}: typowa zmiana {med:.1f}, próg {prog:.1f}, przeskoki: {opis}")
