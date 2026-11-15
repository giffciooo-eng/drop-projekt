"""Reklamy 1 i 2 (statyki) w formatach 4:5 i 9:16. Zapis bez metadanych (ponownie przez Pillow)."""
from pathlib import Path
from PIL import Image
import usnij_grafika as g

TU = Path(__file__).resolve().parent
HF = TU / "hf"
WYJ = TU.parent

FORMATY = {"4x5": (1080, 1350), "9x16": (1080, 1920)}


def zapisz(img, nazwa):
    """Ponowny zapis przez Pillow: same piksele, bez EXIF i innych metadanych."""
    rgb = img.convert("RGB")
    czysty = Image.new("RGB", rgb.size)
    czysty.paste(rgb)
    czysty.save(WYJ / nazwa, "JPEG", quality=92, optimize=True, progressive=True)


def reklama1(fmt):
    w, h = FORMATY[fmt]
    pion = fmt == "9x16"
    tlo = Image.open(HF / f"r1-tlo-{fmt}.jpg")
    img = g.dopasuj(tlo, w, h, fokus_y=0.5)
    m = 64
    gora = 250 if pion else 56          # w 9:16 omijamy pasek z profilem
    g.gradient(img, 0, int(h * (0.42 if pion else 0.46)), alfa_od=230)
    g.logo(img, (m, gora), 44)
    g.etykieta(img, (m, gora + 92), "OBCIĄŻENIOWA MASKA NA OCZY", 25)
    f = g.font("serif", 84 if not pion else 92)
    linie = g.zawin("Ciemność i delikatny ciężar na powiekach.", f, w - 2 * m)
    g.tekst(img, (m, gora + 140), linie, f, g.KREM, odstep=1.08)
    # karta z ceną (niska, żeby nie zasłaniała końców maski)
    kh = 186
    dol = h - (380 if pion else 40)     # w 9:16 omijamy przycisk i opis na dole
    ky = dol - kh
    g.zaokraglony(img, (m - 8, ky, w - m + 8, dol), 26, g.NOC + (238,))
    x = m + 30
    g.tekst(img, (x, ky + 22), ["2 maski"], g.font("sans-bold", 32), g.KREM, cien=False)
    g.przekreslona(img, (x, ky + 74), "278 zł", g.font("sans", 38), g.SZARY_TXT)
    g.tekst(img, (x + 148, ky + 36), ["199 zł"], g.font("serif-bold", 94), g.BURSZTYN, cien=False)
    fx = g.font("sans-semi", 30)
    prawa = w - m - 30
    for i, l in enumerate(["darmowa", "dostawa"]):
        g.tekst(img, (prawa - fx.getlength(l), ky + 50 + i * 40), [l], fx, g.KREM, cien=False)
    g.tekst(img, (x, ky + 148), ["278 zł to cena 2 masek kupionych osobno (2 × 139 zł)"],
            g.font("sans", 21), g.SZARY_TXT, cien=False)
    zapisz(img, f"reklama-1-{fmt}.jpg")


def reklama2(fmt):
    w, h = FORMATY[fmt]
    pion = fmt == "9x16"
    tlo = Image.open(HF / f"r2-tlo-{fmt}.jpg")
    img = g.dopasuj(tlo, w, h, fokus_y=0.55)
    m = 64
    gora = 250 if pion else 56
    g.gradient(img, 0, int(h * (0.42 if pion else 0.40)), alfa_od=246)
    g.logo(img, (m, gora), 44)
    g.etykieta(img, (m, gora + 92), "PREZENT NA ŚWIĘTA", 25)
    f = g.font("serif", 66)
    linie = ["Prezent dla kogoś, kto mówi:", "„znowu nie spałam”."]
    y = g.tekst(img, (m, gora + 140), linie, f, g.KREM, odstep=1.1)
    g.tekst(img, (m, y + 10), ["Jedna maska dla niej, druga dla Ciebie."], g.font("sans-semi", 31), g.KREM)
    kh = 168
    dol = h - (380 if pion else 40)
    ky = dol - kh
    g.zaokraglony(img, (m - 8, ky, w - m + 8, dol), 26, g.NOC + (238,))
    x = m + 30
    g.tekst(img, (x, ky + 20), ["2 maski"], g.font("sans-bold", 32), g.KREM, cien=False)
    g.tekst(img, (x, ky + 52), ["199 zł"], g.font("serif-bold", 94), g.BURSZTYN, cien=False)
    fx = g.font("sans-semi", 30)
    prawa = w - m - 30
    for i, l in enumerate(["darmowa dostawa", "1 maska: 139 zł"]):
        g.tekst(img, (prawa - fx.getlength(l), ky + 50 + i * 42), [l], fx,
                g.KREM if i == 0 else g.SZARY_TXT, cien=False)
    zapisz(img, f"reklama-2-{fmt}.jpg")


if __name__ == "__main__":
    for fmt in FORMATY:
        reklama1(fmt)
        reklama2(fmt)
    print("gotowe")
