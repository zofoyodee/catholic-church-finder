# Catholic Church Finder

An interactive 3D globe of about 184,000 Catholic churches, chapels, shrines, basilicas and cathedrals around the world.

**Live site:** https://churchglobe.com/

- Drag to spin the globe, scroll or pinch to zoom. Pins cluster when zoomed out; church names appear under pins once you zoom into a city.
- Search by church name or town.
- Click a pin to open its details card. The card looks up a photograph of the church live on Wikimedia Commons and Wikipedia (matched by location and name, credited to its photographer). A gold votive candle shows while it loads; churches without a matching photo keep a drawn scene.
- **Guided tours**: the globe flies through Marian shrines, the Camino de Santiago, the great basilicas or the great cathedrals, with a card at each stop. Link straight to one with `?tour=marian`, `camino`, `basilicas` or `cathedrals`.
- **Church of the day**: a card names today's saint or feast and a church dedicated to it. The pill under the title shows the liturgical season, and the page's accent colour follows the colour of the day.
- **Globe view** (layers button): satellite imagery, day and night shading, stars and atmosphere, a density glow, and liturgical colours can each be switched on or off.

## How it works

It is a static site with no build step and no server.

| Path | What it holds |
| --- | --- |
| `index.html` | The whole app (MapLibre GL globe, search, details card, live photo lookup) |
| `data/points.txt` | Base64 positions and types of every church |
| `data/d/N.json` | Details for churches, 2,000 per file, loaded on click |
| `data/search-*.txt` | Search index, loaded on first search |
| `app/engage.js`, `app/engage.css` | Tours, church of the day, liturgical calendar, globe view (stars, night, satellite, density glow, golden cathedral pins) |
| `data/tours.json`, `data/calendar.json` | Tour stops and the saints calendar, built by `scripts/engage/` |
| `data/photos.json`, `photos/N.jpg` | ~80 pre-matched cathedral and basilica photos, used before the live lookup |
| `base/*.json` | Natural Earth basemap (land, borders, cities, rivers) |
| `fonts/*.txt` | Map label glyphs (Latin, Vietnamese, Greek, Cyrillic, Hebrew and Arabic ranges) |
| `base/names/<lang>.json` | City names on the map in each language, from Natural Earth |
| `i18n/<lang>.json` | Interface text in each language; English lives in `index.html` as `EN` |
| `i18n/saints/<lang>.json` | The patron saint bios in each language, `[name, feast, bio]` per English title |
| `scripts/` | The pipeline that built the data from Overture Maps |

## Languages

The page follows the browser's language, and the picker at the top switches it (the choice is remembered, and `?lang=xx` forces one). It speaks English, Spanish, Portuguese, French, Filipino, Italian, Polish, Swahili, German, Chinese, Dutch, Indonesian, Vietnamese, Malayalam, Korean, Hungarian, Ukrainian, Croatian, Arabic and Slovak, chosen by number of Catholic speakers. Arabic is laid out right to left. Wikipedia and Wikidata details come from the reader's own Wikipedia when it has the article, and every language keeps the Catholic-voice filter.

To add a language, add it to `LANGS` in `index.html`, write `i18n/<lang>.json` and `i18n/saints/<lang>.json`, add its Wikipedia's outsider phrases to `OUTSIDER_BY`, and run `python3 scripts/i18n/check.py` (missing keys, placeholders, plural forms and saints). `scripts/i18n/city_names.py` builds the city names. Translations other than English are first drafts and welcome review by native speakers.

## Data

- Places: [Overture Maps](https://docs.overturemaps.org/guides/places/) release 2026-10-21.0, © Overture Maps Foundation, CDLA Permissive 2.0. Places tagged as Roman Catholic places of worship, plus Christian places whose names are clearly Catholic.
- Satellite imagery: [Sentinel-2 cloudless](https://s2maps.eu) by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2020), CC BY-NC-SA 4.0.
- Basemap: [Natural Earth](https://www.naturalearthdata.com/) (public domain).
- Photos: [Wikimedia Commons](https://commons.wikimedia.org/), each under the license shown on the photo's credit.

Coverage is strongest in the Americas and Western Europe and thinner in parts of Africa and Asia.

## Run locally

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```
