"""Every number used in the page, paper, blog and collage (data/results.json), and the page data.

Universe. Glottolog lists 8,618 language-level languoids. 380 'Bookkeeping' entries (names kept for reference, not
languages) are dropped. Of the rest, the analysis of families, endangerment, diversity and speakers uses the spoken first
languages ('Spoken L1 Language'); sign languages, pidgins, mixed, artificial and unclassifiable languages, speech registers
and unattested languages are mapped but grouped as 'not in a family'. A family is a top-level genealogical family in
Glottolog; an isolate is a spoken language with no known relatives; together they are 'lineages'.
'Living' means any endangerment status other than extinct (languages with no status are counted as living).

Page data written here: data/site.json (embedded), data/langs.json, data/tree.json, data/grid.json and data/dialects.json
(loaded by the page). Reusable tables: data/families.csv, data/countries.csv, data/diversity_grid.csv.
"""
import csv, statistics
import numpy as np
from collections import Counter, defaultdict
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

L = jload(f"{WORK}/langs.json")
N = jload(f"{WORK}/nodes.json")
C = jload(f"{WORK}/centres.json")
HL = jload(f"{WORK}/homelands.json")
G = jload(f"{WORK}/grid.json")
CO = jload(f"{WORK}/countries.json")
META = jload(f"{WORK}/meta.json")
pct = lambda a, b: round(100 * a / b, 1) if b else 0.0
SP = [l for l in L if l["cat"] == "Spoken_L1_Language"]
living = lambda l: l["aes"] != 6
lineage = lambda l: l["top"] or l["id"]

R = {"meta": {"doi": DOI, "page": PAGE, "repo": REPO, "blog": BLOG, "retrieved": RETRIEVED, "glottolog": GLOTTOLOG_VERSION,
              "citation": META["glottolog_citation"]}}

# ---------------------------------------------------------------- counts
cats = Counter(l["cat"] for l in L)
tops = [k for k, n in N.items() if n["parent"] is None and not n["pseudo"]]
fam_sp = defaultdict(list)
for l in SP:
    if l["top"]:
        fam_sp[l["top"]].append(l)
iso_l = [l for l in SP if l["isolate"]]
assert len(fam_sp) == len(tops), (len(fam_sp), len(tops))
sizes = sorted(((k, len(v)) for k, v in fam_sp.items()), key=lambda x: -x[1])
top5 = sum(n for _, n in sizes[:5])
R["counts"] = {
    "languoids_language_level": len(L) + 380, "bookkeeping": 380, "mapped": len(L), "spoken": len(SP),
    "sign": cats["Sign_Language"], "pidgin": cats["Pidgin"], "unclassifiable": cats["Unclassifiable"], "unattested": cats["Unattested"],
    "artificial": cats["Artificial_Language"], "mixed": cats["Mixed_Language"], "register": cats["Speech_Register"],
    "other_nonfamily": len(L) - len(SP), "no_coords": sum(1 for l in L if l["lat"] is None),
    "families": len(tops), "isolates": len(iso_l), "lineages": len(tops) + len(iso_l),
    "isolates_living": sum(1 for l in iso_l if living(l)), "isolates_extinct": sum(1 for l in iso_l if l["aes"] == 6),
    "families_living": sum(1 for k, v in fam_sp.items() if any(living(l) for l in v)),
    "families_extinct": sum(1 for k, v in fam_sp.items() if not any(living(l) for l in v)),
    "lineages_living": sum(1 for k, v in fam_sp.items() if any(living(l) for l in v)) + sum(1 for l in iso_l if living(l)),
    "families_le5": sum(1 for _, n in sizes if n <= 5), "families_ge100": sum(1 for _, n in sizes if n >= 100),
    "top5_share": pct(top5, len(SP)), "top5_n": top5,
    "nodes": sum(1 for n in N.values() if not n["pseudo"]), "dialects": sum(l["ndial"] for l in L),
    "max_depth_lang": max(L, key=lambda l: len(l["path"]))["name"], "max_depth": max(len(l["path"]) for l in L),
    "living": sum(1 for l in SP if living(l)),
}
R["top_families"] = [{"id": k, "name": N[k]["name"], "n": n, "pct": pct(n, len(SP)), "living": sum(1 for l in fam_sp[k] if living(l))} for k, n in sizes[:15]]
named_iso = {l["name"]: l["id"] for l in iso_l}
for nm in ("Basque", "Burushaski", "Nihali", "Kusunda", "Zuni", "Sumerian"):
    assert nm in named_iso, nm
R["isolate_examples"] = ["Basque", "Burushaski", "Nihali", "Kusunda", "Zuni", "Sumerian"]
eng = next(l for l in L if l["id"] == "stan1293")
R["english_path"] = [N[x]["name"] for x in eng["path"]]
R["english_depth"] = len(eng["path"])
_ie = {N[k]["name"]: k for k in N if N[k]["parent"] in ("indo1319", "clas1257")}
_cnt = Counter(x for l in SP for x in l["path"])
R["ie_ii"], R["ie_ger"], R["ie_ita"] = _cnt[_ie["Indo-Iranian"]], _cnt[_ie["Germanic"]], _cnt[_ie["Italic"]]

# ---------------------------------------------------------------- endangerment
ac = Counter(l["aes"] or 0 for l in SP)
endg = sum(ac[k] for k in (2, 3, 4, 5))
R["aes"] = {"counts": {AES.get(k, "no data"): ac[k] for k in (1, 2, 3, 4, 5, 6, 0)},
            "pct": {AES.get(k, "no data"): pct(ac[k], len(SP)) for k in (1, 2, 3, 4, 5, 6, 0)},
            "endangered": endg, "endangered_pct": pct(endg, len(SP)), "extinct": ac[6], "extinct_pct": pct(ac[6], len(SP)),
            "endangered_or_extinct_pct": pct(endg + ac[6], len(SP)), "endangered_of_living_pct": pct(endg, len(SP) - ac[6]),
            "severe": ac[4] + ac[5], "severe_pct": pct(ac[4] + ac[5], len(SP)), "safe_pct": pct(ac[1], len(SP)), "nodata": ac[0]}
mac = defaultdict(list)
for l in SP:
    m = l["macro"].split(";")[0] if l["macro"] else ""
    if m:
        mac[m].append(l)
R["macro"] = sorted([{"name": m, "n": len(v), "endangered_pct": pct(sum(1 for l in v if l["aes"] in (2, 3, 4, 5)), len(v)),
                      "extinct_pct": pct(sum(1 for l in v if l["aes"] == 6), len(v)), "safe_pct": pct(sum(1 for l in v if l["aes"] == 1), len(v)),
                      "lineages": len({lineage(l) for l in v}), "lineages_living": len({lineage(l) for l in v if living(l)}),
                      "counts": [sum(1 for l in v if (l["aes"] or 0) == k) for k in (1, 2, 3, 4, 5, 6, 0)]} for m, v in mac.items()], key=lambda x: -x["n"])
R["macro_by"] = {m["name"]: m for m in R["macro"]}
# families entirely endangered or extinct
fam_status = {}
for k, v in fam_sp.items():
    fam_status[k] = "extinct" if all(l["aes"] == 6 for l in v) else ("all_endangered" if all(l["aes"] in (2, 3, 4, 5, 6) for l in v) else "has_safe_or_unknown")
fs = Counter(fam_status.values())
iso_safe = sum(1 for l in iso_l if l["aes"] in (1, None))
R["aes"]["lineages_no_safe"] = fs["extinct"] + fs["all_endangered"] + sum(1 for l in iso_l if l["aes"] in (2, 3, 4, 5, 6))
R["aes"]["lineages_no_safe_pct"] = pct(R["aes"]["lineages_no_safe"], R["counts"]["lineages"])
R["aes"]["families_all_endangered"] = fs["all_endangered"]
R["aes"]["isolates_endangered"] = sum(1 for l in iso_l if l["aes"] in (2, 3, 4, 5))
R["aes"]["isolates_endangered_pct"] = pct(R["aes"]["isolates_endangered"], R["counts"]["isolates_living"])
# documentation
md = Counter(l["med"] for l in SP)
R["med"] = {"wordlist_or_less": md[4], "wordlist_pct": pct(md[4], len(SP)), "grammar_or_more": md[0] + md[1], "grammar_pct": pct(md[0] + md[1], len(SP)),
            "no_grammar_pct": pct(md[2] + md[3] + md[4], len(SP))}

# ---------------------------------------------------------------- speakers (Wikidata)
S = sorted([l for l in SP if l["speakers"]], key=lambda l: -l["speakers"])
tot = sum(l["speakers"] for l in S)
yrs = Counter(int(l["sp_year"]) if l["sp_year"] else None for l in S)
R["speakers"] = {"n": len(S), "coverage_pct": pct(len(S), len(SP)), "coverage_living_pct": pct(len(S), R["counts"]["living"]),
                 "total": tot, "top20_share": pct(sum(l["speakers"] for l in S[:20]), tot), "top10_share": pct(sum(l["speakers"] for l in S[:10]), tot),
                 "top100_share": pct(sum(l["speakers"] for l in S[:100]), tot), "median": statistics.median(l["speakers"] for l in S),
                 "under1000": sum(1 for l in S if l["speakers"] < 1000), "under10000": sum(1 for l in S if l["speakers"] < 10000),
                 "n_undated": yrs[None], "since2015": sum(v for k, v in yrs.items() if k and k >= 2015),
                 "before2000": sum(v for k, v in yrs.items() if k and k < 2000),
                 "top": [{"id": l["id"], "name": l["name"], "n": l["speakers"], "year": l["sp_year"], "family": N[l["top"]]["name"] if l["top"] else "isolate"} for l in S[:25]]}
# languages that hold half the counted speakers
c = 0
for i, l in enumerate(S):
    c += l["speakers"]
    if c >= tot / 2:
        R["speakers"]["half_n"] = i + 1
        break
R["speakers"]["half_share_of_langs_pct"] = round(100 * R["speakers"]["half_n"] / len(SP), 2)
# by family
fs_sp = Counter()
for l in S:
    fs_sp[l["top"] or "isolate"] += l["speakers"]
R["speakers"]["by_family"] = [{"id": k, "name": N[k]["name"] if k in N else "Isolates", "n": v, "pct": pct(v, tot)} for k, v in fs_sp.most_common(10)]
R["speakers"]["endangered_with_count"] = sum(1 for l in S if l["aes"] in (2, 3, 4, 5))
R["speakers"]["safe_with_count_pct"] = pct(sum(1 for l in S if l["aes"] == 1), len(S))
R["speakers"]["safe_overall_pct"] = R["aes"]["safe_pct"]

# ---------------------------------------------------------------- diversity: countries
cl = defaultdict(list)
for l in SP:
    if living(l):
        for c_ in l["countries"]:
            cl[c_].append(l)
crow = []
for k, v in cl.items():
    if k not in CO:
        continue
    a = CO[k]["area"]
    crow.append({"iso": k, "name": CO[k]["name"], "n": len(v), "lineages": len({lineage(l) for l in v}), "families": len({l["top"] for l in v if l["top"]}),
                 "isolates": sum(1 for l in v if l["isolate"]), "area": round(a), "per10k": round(1e4 * len(v) / a, 2),
                 "endangered": sum(1 for l in v if l["aes"] in (2, 3, 4, 5))})
crow.sort(key=lambda x: -x["n"])
big = [c_ for c_ in crow if c_["area"] >= 10000]
R["countries"] = {"top_n": crow[:12], "top_lineages": sorted(crow, key=lambda x: (-x["lineages"], -x["n"]))[:12],
                  "top_density": sorted(big, key=lambda x: -x["per10k"])[:10], "n_countries": len(crow),
                  "one_language_n": sum(1 for c_ in crow if c_["n"] == 1)}
top3 = crow[:3]
R["countries"]["top3_share_pct"] = pct(len({l["id"] for c_ in top3 for l in cl[c_["iso"]]}), R["counts"]["living"])
R["countries"]["png_n"] = next(c_ for c_ in crow if c_["iso"] == "PG")["n"]
R["countries"]["png_lineages"] = next(c_ for c_ in crow if c_["iso"] == "PG")["lineages"]
with open(f"{DATA}/countries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["country_code", "country", "living_languages", "lineages", "families", "isolates", "area_km2", "languages_per_10000km2", "endangered_languages"])
    for c_ in crow:
        w.writerow([c_["iso"], c_["name"], c_["n"], c_["lineages"], c_["families"], c_["isolates"], c_["area"], c_["per10k"], c_["endangered"]])

# ---------------------------------------------------------------- diversity: equal-area grid
from pyproj import Transformer
FWD = Transformer.from_crs(4326, 8857, always_xy=True)
cellL = defaultdict(list)
for l in SP:
    if l["lat"] is None:
        continue
    x, y = FWD.transform(l["lon"], l["lat"])
    cellL[f"{int(np.floor(x / G['cell_m']))},{int(np.floor(y / G['cell_m']))}"].append(l)
missing = [k for k in cellL if k not in G["cells"]]
print("languages in cells without land:", sum(len(cellL[k]) for k in missing), "in", len(missing), "cells (kept; land area set from neighbours = 0)")
A1 = jload(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")["features"]
A1G = [shape(f["geometry"]) for f in A1]
A1T = STRtree(A1G)


def admin1(lat, lon):
    p = Point(lon, lat)
    for i in A1T.query(p):
        if A1G[i].contains(p):
            pr = A1[i]["properties"]
            return pr["name"], pr["admin"]
    i = A1T.nearest(p)
    pr = A1[i]["properties"]
    return pr["name"], pr["admin"]


cells = []
for k, v in cellL.items():
    lv = [l for l in v if living(l)]
    cells.append({"k": k, "n": len(lv), "n_all": len(v), "lin": len({lineage(l) for l in lv}), "lin_all": len({lineage(l) for l in v}),
                  "land": G["cells"].get(k, {}).get("land", 0), "ring": G["cells"].get(k, {}).get("ring")})


def place(c_):
    v = [l for l in cellL[c_["k"]] if living(l)] or cellL[c_["k"]]
    names = Counter(admin1(l["lat"], l["lon"]) for l in v)
    (a, co), _ = names.most_common(1)[0]
    return f"{a}, {co}"


topc = sorted(cells, key=lambda c_: (-c_["n"], -c_["lin"]))[:8]
topl = sorted(cells, key=lambda c_: (-c_["lin"], -c_["n"]))[:8]
for c_ in topc + topl:
    c_["place"] = place(c_)
R["grid"] = {"cell_km": G["cell_m"] // 1000, "n_cells_with": sum(1 for c_ in cells if c_["n"]), 
             "top_n": [{k: c_[k] for k in ("k", "n", "lin", "place", "land")} for c_ in topc],
             "top_lin": [{k: c_[k] for k in ("k", "n", "lin", "place", "land")} for c_ in topl],
             "cells_ge50": sum(1 for c_ in cells if c_["n"] >= 50), "cells_ge10lin": sum(1 for c_ in cells if c_["lin"] >= 10)}
# share of the world's living languages in the densest 1% / 5% of land cells
land_cells = sum(1 for c_ in G["cells"].values() if np.mean([p[0] for p in c_["ring"]]) > -60)   # Antarctica left out
srt = sorted((c_["n"] for c_ in cells), reverse=True)
R["grid"]["n_land_cells"] = land_cells
R["grid"]["top1pct_share"] = pct(sum(srt[:round(land_cells * .01)]), R["counts"]["living"])
R["grid"]["top1pct_cells"] = round(land_cells * .01)
R["grid"]["top5pct_share"] = pct(sum(srt[:round(land_cells * .05)]), R["counts"]["living"])
with open(f"{DATA}/diversity_grid.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["cell", "centre_lat", "centre_lon", "land_km2", "living_languages", "living_lineages", "all_languages", "all_lineages"])
    for c_ in sorted(cells, key=lambda c_: -c_["n"]):
        i, j = map(int, c_["k"].split(","))
        lo, la = Transformer.from_crs(8857, 4326, always_xy=True).transform((i + .5) * G["cell_m"], (j + .5) * G["cell_m"])
        w.writerow([c_["k"], round(la, 3), round(lo, 3), c_["land"], c_["n"], c_["lin"], c_["n_all"], c_["lin_all"]])
jsave({"km": G["cell_m"] // 1000, "c": [[c_["k"], c_["n"], c_["lin"], c_["n_all"], c_["lin_all"], c_["land"], c_["ring"]] for c_ in cells if c_["ring"]]}, f"{DATA}/grid.json")

# ---------------------------------------------------------------- origins
H = HL["H"]
orig = []
for h in H:
    c_ = C[h["node"]]
    orig.append({"family": h["family"], "hyp": h["hyp"], "node": h["node"], "km_hotspot": c_["homeland_km"][h["hyp"]].get("hotspot"),
                 "km_centre": c_["homeland_km"][h["hyp"]]["centre"], "km_branch": c_["homeland_km"][h["hyp"]].get("branch_centre")})
R["origins"] = {"n_hyp": len(H), "n_fam": len({h["family"] for h in H}), "rows": orig,
                "hot_within500": sorted({o["family"] for o in orig if o["km_hotspot"] is not None and o["km_hotspot"] <= 500}),
                "centre": {k: C[k] for k in {h["node"] for h in H}}}
fam_best = {}
for o in orig:
    fam_best[o["family"]] = min(fam_best.get(o["family"], 1e9), o["km_hotspot"])
R["origins"]["n_hot_within500"] = sum(1 for v in fam_best.values() if v <= 500)
R["origins"]["n_hot_within1000"] = sum(1 for v in fam_best.values() if v <= 1000)
R["origins"]["n_centre_within500"] = sum(1 for f_ in fam_best if min(o["km_centre"] for o in orig if o["family"] == f_) <= 500)
R["origins"]["n_compared"] = len(fam_best)
km = lambda fam_, hyp: next(o for o in orig if o["family"] == fam_ and o["hyp"] == hyp)
R["origins"]["an_km"] = km("Austronesian", "Out of Taiwan")["km_hotspot"]
R["origins"]["an_centre_km"] = km("Austronesian", "Out of Taiwan")["km_centre"]
R["origins"]["pn_km"] = km("Pama-Nyungan", "Gulf Plains")["km_hotspot"]
R["origins"]["bantu_km"] = km("Bantu", "Grassfields origin")["km_hotspot"]
R["origins"]["bantu_centre_km"] = km("Bantu", "Grassfields origin")["km_centre"]
R["origins"]["qu_km"] = km("Quechuan", "Central Peru")["km_hotspot"]
R["origins"]["ie"] = C["indo1319"]
R["origins"]["st"] = C["sino1245"]

# ---------------------------------------------------------------- page data
# family colours: hand-picked for the largest and the homeland families; other families get one of a set of muted tones
PAL = {"atla1278": "#E07B27", "aust1307": "#1C9AA8", "indo1319": "#3557B0", "sino1245": "#C8323C", "afro1255": "#D2A21E",
       "nucl1709": "#8C5A2E", "pama1250": "#E8603C", "otom1299": "#B0407A", "aust1305": "#7B4BA8", "taik1256": "#E58FBF",
       "drav1251": "#6FAE3A", "araw1281": "#4E8C5C", "mand1469": "#8E6A4E", "tupi1275": "#2E9E6E", "ural1272": "#5BA4D9",
       "turk1311": "#2A7F62", "utoa1244": "#3C8DBA", "quec1387": "#C99A18", "hmon1336": "#7D8E2A", "cent2225": "#A9763D",
       "nilo1247": "#C46A4C", "maya1287": "#9C2F34", "mong1349": "#5B8F3E", "kart1248": "#8A5BC0", "japo1237": "#D84B6B",
       "nakh1245": "#6A4C9C", "algi1248": "#5677A8", "atha1245": "#4F7FA3", "eski1264": "#79A9C9", "tung1282": "#68A07A",
       "kore1284": "#C04A7A"}
MUTED = ["#A79C8C", "#9AA58E", "#A693A0", "#8FA0A8", "#B0A07E", "#9C8F86", "#8E9C8C", "#A8968A"]
fam_ids = [k for k, _ in sizes]
for k in PAL:
    if k != "koreanic":
        assert k in N, k
famcol = {}
for i, k in enumerate(fam_ids):
    famcol[k] = PAL.get(k, MUTED[i % len(MUTED)])
ISO_COL = "#2B2630"
PSEUDO_COL = "#BDB6AA"
fidx = {k: i for i, k in enumerate(fam_ids)}
node_ids = sorted([k for k in N], key=lambda k: (N[k]["depth"], N[k]["name"]))
nidx = {k: i for i, k in enumerate(node_ids)}
# counts per node (all mapped languages under it) and living counts
ncount, nliv = Counter(), Counter()
for l in L:
    for x in l["path"]:
        ncount[x] += 1
        if living(l):
            nliv[x] += 1
# pseudo families: languages in a pseudo family carry it as path[0]
langs_page = []
for l in L:
    langs_page.append([l["id"], l["name"], None if l["lat"] is None else round(l["lat"], 3), None if l["lon"] is None else round(l["lon"], 3),
                       fidx.get(l["top"], -1) if l["cat"] == "Spoken_L1_Language" else -2, l["aes"] or 0,
                       int(l["speakers"]) if l["speakers"] else 0, l["sp_year"] or "", l["iso"], [nidx[x] for x in l["path"]],
                       l["macro"], ";".join(l["countries"]), l["ndial"], l["wd_label"] if l["wd_label"] and norm(l["wd_label"]) != norm(l["name"]) else "",
                       {"Spoken_L1_Language": "", "Sign_Language": "sign language", "Pidgin": "pidgin", "Unclassifiable": "unclassifiable",
                        "Unattested": "unattested", "Artificial_Language": "artificial language", "Mixed_Language": "mixed language",
                        "Speech_Register": "speech register"}[l["cat"]], l["med"] if l["med"] is not None else -1])
jsave({"cols": ["id", "name", "lat", "lon", "fam", "aes", "sp", "spy", "iso", "path", "macro", "cc", "ndial", "alt", "cat", "med"], "L": langs_page}, f"{DATA}/langs.json")
jsave({"cols": ["id", "name", "parent", "n", "living", "pseudo"],
       "N": [[k, N[k]["name"], nidx[N[k]["parent"]] if N[k]["parent"] else -1, ncount[k], nliv[k], int(N[k]["pseudo"])] for k in node_ids]}, f"{DATA}/tree.json")
D = jload(f"{WORK}/dialects.json")
jsave(D, f"{DATA}/dialects.json")

legend_fams = [k for k in fam_ids if k in PAL][:22]
SITE = {"fams": [[k, N[k]["name"], famcol[k], len(fam_sp[k])] for k in fam_ids], "legend": legend_fams, "iso_col": ISO_COL, "pseudo_col": PSEUDO_COL,
        "aes": {str(k): [AES.get(k, "no data"), AES_COL[k]] for k in (1, 2, 3, 4, 5, 6, 0)},
        "homelands": H, "refs": HL["REFS"],
        "centres": {k: {kk: c_.get(kk) for kk in ("name", "n", "n_living", "centre", "hotspot", "hotspot_lang", "hotspot_branches", "n_branches", "branch_centre", "branches")} for k, c_ in C.items()},
        "countries": {k: {"name": v["name"], "bbox": v["bbox"], "lab": [v["lat"], v["lon"]], "n": next((c_["n"] for c_ in crow if c_["iso"] == k), 0),
                          "lin": next((c_["lineages"] for c_ in crow if c_["iso"] == k), 0)} for k, v in CO.items()}}
jsave(SITE, f"{DATA}/site.json")

with open(f"{DATA}/families.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["glottocode", "family", "spoken_languages", "living", "endangered", "extinct", "no_status", "speakers_wikidata_sum", "languages_with_speaker_count",
                "present_centre_lat", "present_centre_lon", "hotspot_lat", "hotspot_lon", "map_colour"])
    for k in fam_ids:
        v = fam_sp[k]; c_ = C[k]
        w.writerow([k, N[k]["name"], len(v), sum(1 for l in v if living(l)), sum(1 for l in v if l["aes"] in (2, 3, 4, 5)), sum(1 for l in v if l["aes"] == 6),
                    sum(1 for l in v if not l["aes"]), int(sum(l["speakers"] or 0 for l in v)), sum(1 for l in v if l["speakers"]),
                    *c_["centre"], *(c_.get("hotspot") or ["", ""]), famcol[k]])

jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("counts", "aes")}, indent=0)[:3000])
print("top families", [(x["name"], x["n"], x["pct"]) for x in R["top_families"][:10]])
print("countries", [(c_["name"], c_["n"], c_["lineages"]) for c_ in R["countries"]["top_n"][:8]])
print("lineages", [(c_["name"], c_["lineages"], c_["n"]) for c_ in R["countries"]["top_lineages"][:8]])
print("density", [(c_["name"], c_["per10k"], c_["n"]) for c_ in R["countries"]["top_density"][:8]])
print("cells n", [(c_["place"], c_["n"], c_["lin"]) for c_ in R["grid"]["top_n"]])
print("cells lin", [(c_["place"], c_["lin"], c_["n"]) for c_ in R["grid"]["top_lin"]])
print("grid", {k: v for k, v in R["grid"].items() if not isinstance(v, list)})
print("speakers", {k: v for k, v in R["speakers"].items() if not isinstance(v, list)})
print("by fam", [(x["name"], x["pct"]) for x in R["speakers"]["by_family"]])
print("macro", [(m["name"], m["n"], m["endangered_pct"], m["extinct_pct"], m["lineages"]) for m in R["macro"]])
print("origins", R["origins"]["hot_within500"], R["origins"]["n_hot_within500"], R["origins"]["n_hot_within1000"], R["origins"]["n_centre_within500"])
print("med", R["med"])
for f_ in ("langs.json", "tree.json", "grid.json", "dialects.json", "site.json"):
    print(f_, os.path.getsize(f"{DATA}/{f_}") // 1024, "KB")
