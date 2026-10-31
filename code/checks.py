"""Facts stated in words (not as tokens) in the page, paper, blog, collage and Reddit post, checked against the data.
Imported by every build script, so a rerun on changed data fails loudly instead of printing a false sentence."""
import csv
from common import *

R = jload(f"{DATA}/results.json")
L = jload(f"{WORK}/langs.json")
N = jload(f"{WORK}/nodes.json")
C = jload(f"{WORK}/centres.json")
c, a, s = R["counts"], R["aes"], R["speakers"]

# families and isolates
assert [f["name"] for f in R["top_families"][:5]] == ["Atlantic-Congo", "Austronesian", "Indo-European", "Sino-Tibetan", "Afro-Asiatic"]
assert c["families"] + c["isolates"] == c["lineages"]
assert R["english_path"][:7] == ["Indo-European", "Classical Indo-European", "Germanic", "Northwest Germanic", "West Germanic", "North Sea Germanic", "Anglo-Frisian"]
assert R["english_path"][7] == "Anglic"
ISO = {l["name"]: l for l in L if l["isolate"]}
for nm, macro in (("Basque", "Eurasia"), ("Burushaski", "Eurasia"), ("Nihali", "Eurasia"), ("Kusunda", "Eurasia")):
    assert ISO[nm]["aes"] != 6 and ISO[nm]["macro"] == macro, nm
assert ISO["Sumerian"]["aes"] == 6
_b = next(l for l in L if l["name"] == c["max_depth_lang"])
assert _b["countries"] == ["GA"] and "narr1281" in _b["path"]   # a Bantu language of Gabon
# diversity
assert [x["name"] for x in R["countries"]["top_n"][:5]] == ["Papua New Guinea", "Indonesia", "Nigeria", "India", "China"]
assert [x["name"] for x in R["countries"]["top_lineages"][:3]] == ["Papua New Guinea", "Indonesia", "Brazil"]
assert R["countries"]["top_density"][0]["name"] == "Vanuatu" and R["countries"]["top_density"][0]["per10k"] > 3 * R["countries"]["top_density"][1]["per10k"]
assert R["grid"]["top_lin"][0]["place"] == "Sandaun, Papua New Guinea"
places = [x["place"] for x in R["grid"]["top_n"][:8]]
assert sum("Papua New Guinea" in p for p in places) >= 3 and any("Mexico" in p for p in places) and any("Nigeria" in p for p in places) and any("Cameroon" in p for p in places)
rows = list(csv.DictReader(open(f"{DATA}/diversity_grid.csv")))[:30]
assert any(80 < float(r["centre_lon"]) < 100 and 20 < float(r["centre_lat"]) < 30 for r in rows)  # eastern Himalaya
# endangerment
mb = R["macro_by"]
assert mb["Australia"]["extinct_pct"] > mb["South America"]["extinct_pct"] > mb["North America"]["extinct_pct"] > max(mb[k]["extinct_pct"] for k in ("Africa", "Eurasia", "Papunesia"))
assert a["endangered_pct"] > 50
# speakers
assert s["top"][0]["name"] == "Mandarin Chinese" and s["top"][9]["name"] == "Japanese"
assert [x["name"] for x in s["by_family"][:2]] == ["Indo-European", "Sino-Tibetan"]
assert any(x["name"] == "Standard Arabic" for x in s["top"][:20])
# origins
o = R["origins"]
assert o["hot_within500"] == ["Austronesian", "Bantu", "Pama-Nyungan", "Quechuan", "Uto-Aztecan"], o["hot_within500"]
ua = {r["hyp"]: r for r in o["rows"] if r["family"] == "Uto-Aztecan"}
assert ua["Northern origin"]["km_hotspot"] <= 500 < ua["Southern origin"]["km_hotspot"]
ie = C["indo1319"]
assert 13 < ie["hotspot"][1] < 30 and 38 < ie["hotspot"][0] < 46   # the Balkans
br = {}
for l in L:
    if l["top"] == "indo1319" and l["cat"] == "Spoken_L1_Language" and l["lat"] is not None and great_circle_km(*ie["hotspot"], l["lat"], l["lon"]) <= 500 and len(l["path"]) > 2:
        br.setdefault(N[l["path"][2]]["name"], []).append(l["name"])
assert {"Italic", "Balto-Slavic", "Albanian", "Graeco-Phrygian", "Indo-Iranian"} <= set(br), br
assert any("Romani" in x for x in br["Indo-Iranian"]), br["Indo-Iranian"]
for r in o["rows"]:
    if r["family"] == "Indo-European":
        assert r["km_hotspot"] > 1000
st = C["sino1245"]
assert 88 < st["hotspot"][1] < 97 and 22 < st["hotspot"][0] < 29   # north-east India
assert o["rows"][[r["family"] for r in o["rows"]].index("Sino-Tibetan")]["km_hotspot"] > 1000
assert C["aust1307"]["hotspot_lang"] == "Itbayat"
assert "Celtic" in br and len(br) == C["indo1319"]["hotspot_branches"]
for r in o["rows"]:
    if r["family"] in ("Turkic", "Afro-Asiatic"):
        assert min(r["km_hotspot"], r["km_centre"]) > 1000, r
assert -10 < C["narr1281"]["centre"][0] < 2 and 15 < C["narr1281"]["centre"][1] < 28   # Congo basin
mb = R["macro_by"]
assert mb["Africa"]["safe_pct"] == max(m["safe_pct"] for m in R["macro"])
assert mb["Papunesia"]["lineages"] > 100 and mb["South America"]["lineages"] > 100
assert R["ie_ii"] > R["ie_ger"] > R["ie_ita"]
