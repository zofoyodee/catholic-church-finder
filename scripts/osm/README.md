# Church pins from OpenStreetMap (2026-11-03)

The planet file is streamed from the AWS open-data copy (https://osm-pds.s3.amazonaws.com/planet-latest.osm.pbf),
cut into 6 byte ranges that are read in parallel (`rangecat.py` resyncs each range on a blob boundary), and filtered
with osmium-tool. Nothing of the planet is stored on disk.

1. `partsA.sh`: every place of worship, church/chapel/cathedral building, and anything tagged with a Catholic denomination.
2. `parseA.py`: one JSON list (A.json) and the node/way ids needed for locations (idsB.txt, split per range into idsB0..5.txt).
3. `partsB.sh` / `partsC.sh`: the nodes of church outlines, then the nodes of multipolygon churches' outer ways.
4. `locate.py`: one record per church with its building centre, classed `cath` (Catholic denomination), `unk` (no denomination) or `other`.
5. `match.py OSMDIR REPO OUTDIR`: a pin is confirmed when a Catholic or untagged OSM church lies within 150 m and the names agree
   (or it is within 60 m); it moves onto the building and gains OSM's website/phone/Wikidata id (record field 14).
   Unconfirmed pins become type 7 (hidden); a second pin with a similar name on the same building becomes a `dup` override.
   Named OSM Catholic churches that no pin matched are appended (indexes stay stable for older pins). Writes points.txt, d/, search, meta, overrides.
6. Dev: copy OUTDIR into `<source>/dev-data/` and run `scripts/dev/build.py <source> dev`.

`index-osm.patch` holds the page changes (credits, About text, OSM source line, Wikidata photo lookup) that go to the live index.html with the data.
Data © OpenStreetMap contributors, ODbL.
