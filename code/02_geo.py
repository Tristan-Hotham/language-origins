"""Geography: world outlines and place names for the map, country areas, and an equal-area grid for diversity.

Writes
- data/world.json: simplified Natural Earth 1:50m country outlines (iso = ISO 3166-1 alpha-2 where it has one, as Glottolog
  uses, otherwise the Natural Earth ADM0_A3 code).
- data/cities.json: place names for the map (Natural Earth populated places).
- work/countries.json: name, area (km2, Equal Earth projection) and label point for each country code.
- work/grid.json: 200 km x 200 km cells of the Equal Earth projection (EPSG:8857, equal area) that touch land, with their
  land area (Natural Earth 1:50m land) and corner coordinates in longitude and latitude.
"""
import numpy as np
from shapely.geometry import shape, mapping, box
from shapely.ops import transform as stransform, unary_union
from shapely.strtree import STRtree
from pyproj import Transformer
from common import *

FWD = Transformer.from_crs(4326, 8857, always_xy=True)
INV = Transformer.from_crs(8857, 4326, always_xy=True)
proj = lambda g: stransform(lambda x, y, z=None: FWD.transform(np.clip(x, -180, 180), y), g)

NE = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
feats, countries = [], {}
for f in NE:
    p = f["properties"]
    if p["ADM0_A3"] == "ATA":
        continue
    code = p["ISO_A2_EH"] if p["ISO_A2_EH"] not in ("-99", None) else p["ADM0_A3"]
    g0 = shape(f["geometry"]).buffer(0)
    big = max(g0.geoms, key=lambda x: x.area) if g0.geom_type == "MultiPolygon" else g0
    pt = big.representative_point()
    area = proj(g0).area / 1e6
    if code in countries:   # a few codes appear twice in Natural Earth; add the areas
        countries[code]["area"] += area
    else:
        countries[code] = {"name": p["NAME"], "area": area, "lon": round(pt.x, 2), "lat": round(pt.y, 2), "pop": int(p["POP_EST"] or 0),
                           "bbox": [round(v, 2) for v in big.bounds]}
    g = g0.simplify(0.06, preserve_topology=True)
    if g.is_empty:
        continue
    gm = mapping(g)

    def rnd(o):
        if isinstance(o, (list, tuple)):
            if o and isinstance(o[0], (int, float)):
                return [round(o[0], 2), round(o[1], 2)]
            return [rnd(x) for x in o]
        return o
    feats.append({"type": "Feature", "properties": {"iso": code, "name": p["NAME"]},
                  "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")
jsave(countries, f"{WORK}/countries.json")
print("world.json", os.path.getsize(f"{DATA}/world.json") // 1024, "KB;", len(countries), "country codes")

# ---- place names
pp = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
cities = []
for f in pp:
    p = f["properties"]
    pop = p["pop_max"] or 0
    if pop >= 150000 or p["adm0cap"]:
        cities.append({"name": p["name"], "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop)})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
print(len(cities), "place names")

# ---- equal-area grid of 200 km cells on land
CELL = 200_000
land = [proj(shape(f["geometry"]).buffer(0)) for f in jload(f"{GEO}/ne_50m_land.geojson")["features"]]
land = [g.buffer(0) for g in land if not g.is_empty]
tree = STRtree(land)
xmin, xmax = -17_243_959, 17_243_959
ymin, ymax = -8_392_928, 8_392_928
cells = {}
for i in range(int(np.floor(xmin / CELL)), int(np.ceil(xmax / CELL))):
    for j in range(int(np.floor(ymin / CELL)), int(np.ceil(ymax / CELL))):
        b = box(i * CELL, j * CELL, (i + 1) * CELL, (j + 1) * CELL)
        hit = tree.query(b)
        if len(hit) == 0:
            continue
        a = sum(land[k].intersection(b).area for k in hit) / 1e6
        if a <= 0:
            continue
        # corners and edge midpoints back to lon/lat (cells outside the projection's domain are skipped)
        xs = [i * CELL, (i + .5) * CELL, (i + 1) * CELL, (i + 1) * CELL, (i + 1) * CELL, (i + .5) * CELL, i * CELL, i * CELL]
        ys = [j * CELL, j * CELL, j * CELL, (j + .5) * CELL, (j + 1) * CELL, (j + 1) * CELL, (j + 1) * CELL, (j + .5) * CELL]
        lo, la = INV.transform(xs, ys)
        if not np.all(np.isfinite(lo)) or np.max(np.abs(lo)) > 180.5 or np.ptp(lo) > 60:   # also cells split by the antimeridian
            continue
        cells[f"{i},{j}"] = {"land": round(a), "ring": [[round(y, 3), round(x, 3)] for x, y in zip(lo, la)]}
jsave({"cell_m": CELL, "cells": cells}, f"{WORK}/grid.json")
print(len(cells), "land cells")
