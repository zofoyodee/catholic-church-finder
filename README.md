# Catholic Church Finder

An interactive 3D globe of about 184,000 Catholic churches, chapels, shrines, basilicas and cathedrals around the world.

**Live site:** https://zofoyodee.github.io/catholic-church-finder/

- Drag to spin the globe, scroll or pinch to zoom. Pins cluster when zoomed out; church names appear under pins once you zoom into a city.
- Search by church name or town.
- Click a pin to open its details card. The card looks up a photograph of the church live on Wikimedia Commons and Wikipedia (matched by location and name, credited to its photographer). A gold votive candle shows while it loads; churches without a matching photo keep a drawn scene.

## How it works

It is a static site with no build step and no server.

| Path | What it holds |
| --- | --- |
| `index.html` | The whole app (MapLibre GL globe, search, details card, live photo lookup) |
| `data/points.txt` | Base64 positions and types of every church |
| `data/d/N.json` | Details for churches, 2,000 per file, loaded on click |
| `data/search-*.txt` | Search index, loaded on first search |
| `data/photos.json`, `photos/N.jpg` | ~80 pre-matched cathedral and basilica photos, used before the live lookup |
| `base/*.json` | Natural Earth basemap (land, borders, cities, rivers) |
| `fonts/*.txt` | Map label glyphs (Latin range) |
| `scripts/` | The pipeline that built the data from Overture Maps |

## Data

- Places: [Overture Maps](https://docs.overturemaps.org/guides/places/) release 2026-10-21.0, © Overture Maps Foundation, CDLA Permissive 2.0. Places tagged as Roman Catholic places of worship, plus Christian places whose names are clearly Catholic.
- Basemap: [Natural Earth](https://www.naturalearthdata.com/) (public domain).
- Photos: [Wikimedia Commons](https://commons.wikimedia.org/), each under the license shown on the photo's credit.

Coverage is strongest in the Americas and Western Europe and thinner in parts of Africa and Asia.

## Run locally

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```
