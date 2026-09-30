# ZASADY

Obowiązują w całym projekcie. Czytasz ten plik na początku każdego kroku.

Projekt: sklep dropshippingowy na Shopify. Sprzedaż z ruchu organicznego: krótkie klipy na TikToku, Instagram Reels i Facebook Reels. Bez płatnych reklam.

## Narzędzia

- Używasz wyłącznie tych konektorów: Higgsfield, Shopify, Winning Hunter i Facebook (biblioteka reklam).
- Z Facebooka bierzesz tylko bibliotekę reklam. Nie tworzysz kampanii, reklam ani promowanych postów.
- Lokalnie używasz tylko darmowych narzędzi: ffmpeg, yt-dlp, openai-whisper, Python z biblioteką Pillow, jq oraz font Montserrat Bold.
- Żadnych płatnych API ani zewnętrznych scraperów. Jeśli czegoś nie da się zrobić bez nich, mówisz to wprost zamiast kombinować.

## Kredyty w Higgsfield

- Przed każdą generacją obrazu, wideo albo głosu sprawdzasz koszt w kredytach i podajesz mi sumę, zanim ruszysz.
- Po każdym kroku podajesz saldo.

## Cudze materiały

- Kopiujemy koncept, nigdy cudzy materiał. W naszych klipach i na stronie nie ma cudzego wideo, cudzych zdjęć, logo ani nazw marek.

## Język

- Wszystko po polsku, dla polskiego odbiorcy.
- Zdania krótkie, mówione. Zero kalk z angielskiego i słów z reklam („rewolucyjny”, „innowacyjny”).

## Fakty

- Nie wymyślasz liczb ani opinii klientów. Jeśli czegoś nie widzisz, piszesz „brak danych”.

## Jakość

- Każdy wygenerowany obraz i każde wideo oglądasz sam, zanim mi je pokażesz.
- Nieudane próby zapisujesz w nieudane/ z jednym zdaniem, co nie wyszło.

## Raporty

- Jedna rekomendacja z uzasadnieniem, nie pięć opcji do wyboru.
- Po każdym kroku raport w trzech zdaniach: co zrobiłeś, co wyszło, czego potrzebujesz ode mnie.

## Pliki

Trzymamy je płasko w tym folderze.

| Plik | Zawartość |
|---|---|
| produkt.md | wynik szukania produktu |
| referencja.mp4 | klip do odtworzenia konceptu |
| produkt_1.jpg | zdjęcie produktu |
| persona.md | dla kogo i jakim językiem |
| skrypt.md | skrypt klipu |
| gotowe/ | klipy do publikacji |
| nieudane/ | odrzucone próby |
| Montserrat-Bold.ttf | font do napisów (z Google Fonts, ma wszystkie polskie znaki) |

## Środowisko

- Pracujemy w kontenerze w chmurze. Co nie trafi do GitHuba (commit i push), znika razem z kontenerem, więc po każdym kroku zapisujesz pracę w repozytorium.
- Narzędzia doinstalowane w trakcie sesji też znikają. Na stałe instaluje je skrypt startowy środowiska (Setup script w ustawieniach środowiska).
