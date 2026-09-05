#!/usr/bin/env python3
"""
fetch_ticker.py

Junta noticias de Santa Rosa/Barberena desde varias fuentes RSS y escribe
assets/data/ticker.json para el news-ticker de BMM.

Fuentes:
  - AGN, categoría Santa Rosa (ya viene filtrada en origen)
  - Prensa Libre, feed nacional (se filtra por palabras clave acá)
  - Google News, búsqueda por palabras clave

Corre bajo GitHub Actions con un cron. No requiere llaves ni credenciales.

Dependencia: feedparser (pip install feedparser)
"""

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import feedparser

OUTPUT_PATH = Path("assets/data/ticker.json")
MANUAL_PATH = Path("assets/data/ticker-manual.json")

MAX_ITEMS = 20
MAX_AGE_DAYS = 4

# Palabras que activan la categoría "denuncia" en el punto de color del ticker.
DENUNCIA_KEYWORDS = [
    "guatecompras", "denuncia", "denuncian", "corrupcion", "irregular",
    "fiscalia", "ministerio publico", "auditoria", "contrato", "adjudic",
    "desvio de fondos", "sin oferentes",
]

# Palabras/lugares que confirman que la nota es de Santa Rosa/Barberena.
# (Necesario para Prensa Libre y Google News, que no vienen pre-filtrados.)
LOCATION_KEYWORDS = [
    "barberena", "santa rosa", "cuilapa", "el cerinal", "chiquimulilla",
    "taxisco", "nueva santa rosa", "pueblo nuevo vinas", "casillas",
    "san rafael las flores", "santa cruz naranjo", "oratorio",
]

SOURCES = {
    "agn": "https://agn.gt/category/santa-rosa/feed/",
    "prensa_libre": "https://www.prensalibre.com/feed/",
    # Cubre todo el Suroriente, no solo Barberena/Santa Rosa -> necesita el
    # mismo filtro por palabra clave que Prensa Libre. Verificar una vez en
    # el navegador que esta URL responde con XML antes de confiar en ella.
    "visor_suroriente": "https://visorgt.com/feed/",
    "google_news": (
        "https://news.google.com/rss/search?q="
        + quote('"Barberena" OR "Santa Rosa" Guatemala')
        + "&hl=es-419&gl=GT&ceid=GT:es-419"
    ),
}


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def normalize(text: str) -> str:
    return strip_accents(text or "").lower()


def mentions_location(text: str) -> bool:
    normalized = normalize(text)
    return any(kw in normalized for kw in LOCATION_KEYWORDS)


def classify(text: str) -> str:
    normalized = normalize(text)
    if any(kw in normalized for kw in DENUNCIA_KEYWORDS):
        return "denuncia"
    return "comunidad"


def parse_entry_date(entry):
    for field in ("published_parsed", "updated_parsed"):
        value = entry.get(field)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def fetch_source(name: str, url: str, require_location_filter: bool):
    items = []
    parsed = feedparser.parse(url)
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        if require_location_filter and not mentions_location(title):
            continue

        published = parse_entry_date(entry)

        items.append({
            "text": title,
            "cat": classify(title),
            "url": link,
            "source": name,
            "published": published.isoformat() if published else None,
        })
    return items


def load_manual_items():
    if not MANUAL_PATH.exists():
        return []
    try:
        data = json.loads(MANUAL_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    items = []
    for entry in data:
        items.append({
            "text": entry["text"],
            "cat": entry.get("cat", "comunidad"),
            "url": entry.get("url", "#"),
            "source": entry.get("source", "manual"),
            "published": entry.get("published"),
        })
    return items


def dedupe(items):
    seen = set()
    result = []
    for item in items:
        key = normalize(item["text"])[:80]
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def sort_key(item):
    if item["published"]:
        return item["published"]
    return ""  # sin fecha va al final


def main():
    all_items = []

    all_items += fetch_source("agn", SOURCES["agn"], require_location_filter=False)
    all_items += fetch_source("prensa_libre", SOURCES["prensa_libre"], require_location_filter=True)
    all_items += fetch_source("visor_suroriente", SOURCES["visor_suroriente"], require_location_filter=True)
    all_items += fetch_source("google_news", SOURCES["google_news"], require_location_filter=True)
    all_items += load_manual_items()  # para cualquier fuente sin RSS que quieras sumar a mano

    all_items = dedupe(all_items)
    all_items.sort(key=sort_key, reverse=True)
    all_items = all_items[:MAX_ITEMS]

    # El ticker no necesita el campo "published" ni "source" en pantalla,
    # pero los dejamos por si querés depurar o mostrar la fuente después.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Escribí {len(all_items)} noticias en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
