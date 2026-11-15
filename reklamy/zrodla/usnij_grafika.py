"""Usnij: wspólne elementy reklam (fonty, kolory, napisy, cena, plansza końcowa).

Napisy rysujemy sami w Pillow (modele AI psują polskie znaki).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TU = Path(__file__).resolve().parent
FONTY = TU / "fonty"

NOC = (22, 27, 46)          # #161b2e
KREM = (247, 242, 234)      # #f7f2ea
BURSZTYN = (226, 163, 85)   # #e2a355
SZARY_TXT = (176, 172, 190)


def font(nazwa, rozmiar):
    pliki = {
        "serif": "Fraunces_600SemiBold.ttf",
        "serif-bold": "Fraunces_700Bold.ttf",
        "serif-italic": "Fraunces_400Regular_Italic.ttf",
        "sans": "Inter-Medium.otf",
        "sans-semi": "Inter-SemiBold.otf",
        "sans-bold": "Inter-Bold.otf",
    }
    return ImageFont.truetype(str(FONTY / pliki[nazwa]), rozmiar)


def zawin(tekst, fnt, szer):
    """Dzieli tekst na linie mieszczące się w szerokości szer."""
    linie, akt = [], ""
    for slowo in tekst.split():
        proba = (akt + " " + slowo).strip()
        if fnt.getlength(proba) <= szer or not akt:
            akt = proba
        else:
            linie.append(akt)
            akt = slowo
    if akt:
        linie.append(akt)
    # „sierotki”: krótkie słowo (do 2 liter) na końcu linii przenosimy do następnej
    for i in range(len(linie) - 1):
        ost = linie[i].split()
        if len(ost) > 1 and len(ost[-1]) <= 2:
            linie[i] = " ".join(ost[:-1])
            linie[i + 1] = ost[-1] + " " + linie[i + 1]
    return linie


def tekst(img, xy, linie, fnt, kolor, odstep=1.12, cien=True, wyrownanie="lewo", szer=None):
    """Rysuje linie tekstu z delikatnym cieniem. Zwraca dolną krawędź."""
    d = ImageDraw.Draw(img)
    x0, y = xy
    wys = fnt.size * odstep
    if cien:
        warstwa = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(warstwa)
        yy = y
        for l in linie:
            x = x0 if wyrownanie == "lewo" else x0 + (szer - fnt.getlength(l)) / 2
            dc.text((x, yy + 3), l, font=fnt, fill=(0, 0, 0, 150))
            yy += wys
        warstwa = warstwa.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(warstwa)
        d = ImageDraw.Draw(img)
    for l in linie:
        x = x0 if wyrownanie == "lewo" else x0 + (szer - fnt.getlength(l)) / 2
        d.text((x, y), l, font=fnt, fill=kolor)
        y += wys
    return y


def gradient(img, od_y, do_y, kolor=NOC, alfa_od=235, alfa_do=0):
    """Pionowy gradient (np. ciemna góra pod nagłówek)."""
    w, _ = img.size
    warstwa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(warstwa)
    n = max(1, abs(do_y - od_y))
    krok = 1 if do_y > od_y else -1
    for i, y in enumerate(range(od_y, do_y, krok)):
        a = int(alfa_od + (alfa_do - alfa_od) * (i / n) ** 1.2)
        d.line([(0, y), (w, y)], fill=kolor + (a,))
    img.alpha_composite(warstwa)


def logo(img, xy, rozmiar=46, kolor=KREM):
    d = ImageDraw.Draw(img)
    f = font("serif-bold", rozmiar)
    d.text(xy, "usnij", font=f, fill=kolor)
    x = xy[0] + f.getlength("usnij")
    d.text((x, xy[1]), ".", font=f, fill=BURSZTYN)


def etykieta(img, xy, txt, rozmiar=26, kolor=BURSZTYN, rozstaw=3):
    d = ImageDraw.Draw(img)
    f = font("sans-bold", rozmiar)
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=kolor)
        x += f.getlength(ch) + rozstaw


def zaokraglony(img, box, promien, kolor):
    warstwa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(warstwa).rounded_rectangle(box, promien, fill=kolor)
    img.alpha_composite(warstwa)


def przekreslona(img, xy, txt, fnt, kolor):
    d = ImageDraw.Draw(img)
    d.text(xy, txt, font=fnt, fill=kolor)
    x, y = xy
    l, t, r, b = d.textbbox(xy, txt, font=fnt)
    ym = (t + b) / 2 + 2
    d.line([(l - 4, ym), (r + 4, ym)], fill=kolor, width=max(3, fnt.size // 12))


def dopasuj(src, w, h, fokus_y=0.5):
    """Skaluje i przycina obraz do w×h (cover), z punktem skupienia w pionie."""
    im = src.convert("RGB")
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = int(min(max((nh - h) * fokus_y, 0), nh - h))
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


def plansza_koncowa(w, h, packshot_path):
    """2-sekundowa plansza: marka, produkt, cena (ta sama dla wszystkich wideo)."""
    img = Image.new("RGBA", (w, h), NOC + (255,))
    pion = h > w * 1.4
    # karta z packshotem
    kw = int(w * 0.72)
    kh = int(kw * 0.62)
    kx = (w - kw) // 2
    ky = int(h * (0.20 if pion else 0.13))
    zaokraglony(img, (kx, ky, kx + kw, ky + kh), 28, KREM + (255,))
    p = Image.open(packshot_path).convert("RGB")
    # przycinamy pusty brzeg packshotu, żeby maska była duża
    s = p.width
    p = p.crop((int(s * 0.03), int(s * 0.22), int(s * 0.97), int(s * 0.80)))
    p = p.resize((kw - 40, int((kw - 40) * p.height / p.width)), Image.LANCZOS)
    if p.height > kh - 30:
        p = p.resize((int(p.width * (kh - 30) / p.height), kh - 30), Image.LANCZOS)
    img.paste(p, (kx + (kw - p.width) // 2, ky + (kh - p.height) // 2))
    # marka
    f_logo = font("serif-bold", int(w * 0.13))
    lw = f_logo.getlength("usnij.")
    y = ky + kh + int(h * (0.05 if pion else 0.035))
    logo(img, ((w - lw) / 2, y), int(w * 0.13))
    y += int(w * 0.13 * 1.25)
    f1 = font("sans", int(w * 0.036))
    tekst(img, (0, y), ["Obciążeniowa maska na oczy"], f1, SZARY_TXT, cien=False, wyrownanie="srodek", szer=w)
    y += int(w * 0.036 * 1.9)
    f2 = font("serif", int(w * 0.075))
    tekst(img, (0, y), ["2 maski 199 zł"], f2, BURSZTYN, cien=False, wyrownanie="srodek", szer=w)
    y += int(w * 0.075 * 1.3)
    f3 = font("sans-semi", int(w * 0.034))
    tekst(img, (0, y), ["darmowa dostawa · 1 maska 139 zł"], f3, KREM, cien=False, wyrownanie="srodek", szer=w)
    return img
