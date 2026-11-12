// Usnij: logika podglądu (kolory, zestawy, ceny, galeria, przyklejony pasek).
// Ceny zgodne z biznes.md (sekcja Cena i oferta, 12.11.2026).
const OFERTA = {
  1: { cena: 139, dostawa: 12.99, tytul: "1 maska", opis: "139 zł za sztukę" },
  2: { cena: 199, dostawa: 0, tytul: "2 maski", opis: "99,50 zł za sztukę · oszczędzasz 79 zł" },
};
const KOLORY = { Czarny: "#1d1d22", Szary: "#9b9ca3", "Różowy": "#e8b8c4" };
const ZDJECIA = { Czarny: "img/packshot-czarna.jpg", Szary: "img/packshot-szara.jpg", "Różowy": "img/packshot-rozowa.jpg" };

const zl = (n) => (Number.isInteger(n) ? String(n) : n.toFixed(2).replace(".", ",")) + " zł";
const state = { kolor: "Szary", zestaw: 1 };

function render() {
  const o = OFERTA[state.zestaw];
  document.querySelectorAll("[data-price]").forEach((el) => (el.textContent = zl(o.cena)));
  document.querySelectorAll("[data-ship]").forEach((el) => {
    el.textContent = o.dostawa ? "+ " + zl(o.dostawa) + " dostawa" : "Darmowa dostawa";
    el.classList.toggle("free", !o.dostawa);
  });
  document.querySelectorAll("[data-total]").forEach((el) => (el.textContent = zl(o.cena + o.dostawa)));
  document.querySelectorAll("[data-color-name]").forEach((el) => (el.textContent = state.kolor));
  document.querySelectorAll("[data-set-name]").forEach((el) => (el.textContent = o.tytul));
  document.querySelectorAll("[data-atc-label]").forEach((el) => (el.textContent = "Dodaj do koszyka · " + zl(o.cena)));
  document.querySelectorAll(".sw").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.kolor === state.kolor)));
  document.querySelectorAll(".set").forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.zestaw) === state.zestaw)));
}

document.addEventListener("click", (e) => {
  const sw = e.target.closest(".sw");
  if (sw) {
    state.kolor = sw.dataset.kolor; render();
    const main = document.querySelector(".gal-main");
    if (main) main.innerHTML = `<img data-color-img src="${ZDJECIA[state.kolor]}" alt="Maska Usnij, kolor ${state.kolor.toLowerCase()}">`;
    document.querySelectorAll("[data-color-img]").forEach((img) => (img.src = ZDJECIA[state.kolor]));
    document.querySelectorAll(".thumb").forEach((t) => t.setAttribute("aria-current", String(t.dataset.kolorThumb === state.kolor)));
  }
  const set = e.target.closest(".set");
  if (set) { state.zestaw = Number(set.dataset.zestaw); render(); }
  const th = e.target.closest(".thumb");
  if (th) {
    if (th.dataset.kolorThumb) { state.kolor = th.dataset.kolorThumb; render(); }
    document.querySelectorAll(".thumb").forEach((t) => t.setAttribute("aria-current", String(t === th)));
    const main = document.querySelector(".gal-main");
    if (main) main.innerHTML = th.dataset.html;
  }
  const atc = e.target.closest("[data-atc]");
  if (atc) {
    const o = OFERTA[state.zestaw];
    toast(`Podgląd: dodano ${o.tytul} (${state.kolor}) za ${zl(o.cena)}. Prawdziwy koszyk zadziała po wgraniu do Shopify.`);
  }
});

function toast(msg) {
  const t = document.querySelector(".toast");
  if (!t) return;
  t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 3200);
}

// Przyklejony pasek: pojawia się, gdy główny przycisk zniknie z ekranu (po przewinięciu w dół).
const mainAtc = document.querySelector("#main-atc");
const sticky = document.querySelector(".sticky");
if (mainAtc && sticky) {
  const check = () => sticky.classList.toggle("show", mainAtc.getBoundingClientRect().bottom < 0);
  window.addEventListener("scroll", check, { passive: true });
  window.addEventListener("resize", check);
  check();
}

// Miniatury: zapamiętaj zawartość do podmiany w głównym zdjęciu.
document.querySelectorAll(".thumb").forEach((t) => {
  if (!t.dataset.html) t.dataset.html = t.querySelector("template")?.innerHTML || "";
});
render();
