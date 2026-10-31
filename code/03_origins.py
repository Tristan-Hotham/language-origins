"""Origins: proposed homelands from the literature, and two centres computed from Glottolog for every family.

1. data/homelands_literature.csv: proposed homelands and approximate dates for eleven large families, typed in from the
   published sources cited in each row. Places are approximate centres of the regions those sources propose, not exact
   points; dates are the ranges or point estimates they give, in years before the present. Where the literature is split,
   each main hypothesis is a separate row. These are contested hypotheses, not findings of this study.

2. data/family_centres.csv: for each of Glottolog's top-level families (and for Narrow Bantu, so that it can be set beside
   the Bantu homeland):
   - present centre: the spherical mean of the coordinates of the family's living spoken languages (all its languages if
     none is living), i.e. the centre of gravity of where the family is spoken today;
   - diversity hotspot: the deepest-branch hotspot. The family's 'deep branches' are its first-level subgroups (ignoring
     Glottolog's 'Unclassified ...' holding groups); while there are at most two and one holds 80% or more of the languages,
     that branch is replaced by its own subgroups (so Indo-European is split below 'Classical Indo-European' and Turkic below
     'Common Turkic'). The hotspot is the location of the language (living or extinct) with the most distinct deep branches
     within 500 km, ties broken by the number of languages within 500 km and then by closeness to the branch centre;
   - branch centre: the spherical mean of the deep branches' own centres, each branch weighted equally.
   The idea behind the hotspot is the old 'centre of gravity' principle of Sapir (1916): a family has usually been in the
   place where its deepest branches are most diverse for longest. It is a heuristic, not proof: migration, extinction and
   uneven documentation all move it.
"""
import csv, math
import numpy as np
from collections import defaultdict, Counter
from common import *

L = jload(f"{WORK}/langs.json")
N = jload(f"{WORK}/nodes.json")
SP = [l for l in L if l["cat"] == "Spoken_L1_Language" and l["lat"] is not None]

# ------------------------------------------------------------------ 1. literature
REFS = {
    "anthony2007": "Anthony, D. W. (2007) The Horse, the Wheel, and Language: How Bronze-Age Riders from the Eurasian Steppes Shaped the Modern World. Princeton University Press.",
    "anthony2015": "Anthony, D. W. and Ringe, D. (2015) The Indo-European homeland from linguistic and archaeological perspectives. Annual Review of Linguistics 1, 199-219.",
    "haak2015": "Haak, W. et al. (2015) Massive migration from the steppe was a source for Indo-European languages in Europe. Nature 522, 207-211.",
    "renfrew1987": "Renfrew, C. (1987) Archaeology and Language: The Puzzle of Indo-European Origins. Jonathan Cape.",
    "bouckaert2012": "Bouckaert, R. et al. (2012) Mapping the origins and expansion of the Indo-European language family. Science 337, 957-960.",
    "heggarty2023": "Heggarty, P. et al. (2023) Language trees with sampled ancestors support a hybrid model for the origin of Indo-European languages. Science 381, eabg0818.",
    "blust1999": "Blust, R. (1999) Subgrouping, circularity and extinction: some issues in Austronesian comparative linguistics. In Zeitoun, E. and Li, P. J.-K. (eds) Selected Papers from the Eighth International Conference on Austronesian Linguistics. Academia Sinica, 31-94.",
    "gray2009": "Gray, R. D., Drummond, A. J. and Greenhill, S. J. (2009) Language phylogenies reveal expansion pulses and pauses in Pacific settlement. Science 323, 479-483.",
    "vansina1995": "Vansina, J. (1995) New linguistic evidence and 'the Bantu expansion'. Journal of African History 36, 173-195.",
    "grollemund2015": "Grollemund, R. et al. (2015) Bantu expansion shows that habitat alters the route and pace of human dispersals. Proceedings of the National Academy of Sciences 112, 13296-13301.",
    "honkola2013": "Honkola, T. et al. (2013) Cultural and climatic changes shape the evolutionary history of the Uralic languages. Journal of Evolutionary Biology 26, 1244-1253.",
    "grunthal2022": "Grünthal, R., Heyd, V., Holopainen, S., Janhunen, J., Khanina, O., Miestamo, M., Nichols, J., Saarikivi, J. and Sinnemäki, K. (2022) Drastic demographic events triggered the Uralic spread. Diachronica 39(4), 490-524.",
    "janhunen2009": "Janhunen, J. (2009) Proto-Uralic: what, where, and when? In Ylikoski, J. (ed.) The Quasquicentennial of the Finno-Ugrian Society. Mémoires de la Société Finno-Ougrienne 258, 57-78.",
    "golden1992": "Golden, P. B. (1992) An Introduction to the History of the Turkic Peoples. Harrassowitz.",
    "savelyev2020": "Savelyev, A. and Robbeets, M. (2020) Bayesian phylolinguistics infers the internal structure and the time-depth of the Turkic language family. Journal of Language Evolution 5(1), 39-53. doi:10.1093/jole/lzz010",
    "zhang2019": "Zhang, M., Yan, S., Pan, W. and Jin, L. (2019) Phylogenetic evidence for Sino-Tibetan origin in northern China in the Late Neolithic. Nature 569, 112-115.",
    "sagart2019": "Sagart, L. et al. (2019) Dated language phylogenies shed light on the ancestry of Sino-Tibetan. Proceedings of the National Academy of Sciences 116, 10317-10322.",
    "ehret1995": "Ehret, C. (1995) Reconstructing Proto-Afroasiatic (Proto-Afrasian): Vowels, Tone, Consonants, and Vocabulary. University of California Press.",
    "ehret2004": "Ehret, C., Keita, S. O. Y. and Newman, P. (2004) The origins of Afroasiatic. Science 306, 1680-1681.",
    "militarev2002": "Militarev, A. (2002) The prehistory of a dispersal: the Proto-Afrasian (Afroasiatic) farming lexicon. In Bellwood, P. and Renfrew, C. (eds) Examining the Farming/Language Dispersal Hypothesis. McDonald Institute for Archaeological Research, 135-150.",
    "williamson2000": "Williamson, K. and Blench, R. (2000) Niger-Congo. In Heine, B. and Nurse, D. (eds) African Languages: An Introduction. Cambridge University Press, 11-42.",
    "guldemann2018": "Güldemann, T. (2018) Historical linguistics and genealogical language classification in Africa. In Güldemann, T. (ed.) The Languages and Linguistics of Africa. De Gruyter Mouton, 58-444.",
    "bouckaert2018": "Bouckaert, R. R., Bowern, C. and Atkinson, Q. D. (2018) The origin and expansion of Pama-Nyungan languages across Australia. Nature Ecology and Evolution 2, 741-749.",
    "hill2001": "Hill, J. H. (2001) Proto-Uto-Aztecan: a community of cultivators in central Mexico? American Anthropologist 103, 913-934.",
    "fowler1983": "Fowler, C. S. (1983) Some lexical clues to Uto-Aztecan prehistory. International Journal of American Linguistics 49, 224-257.",
    "torero1964": "Torero, A. (1964) Los dialectos quechuas. Anales Científicos de la Universidad Agraria 2, 446-478.",
    "adelaar2004": "Adelaar, W. F. H. with Muysken, P. C. (2004) The Languages of the Andes. Cambridge University Press.",
    "sapir1916": "Sapir, E. (1916) Time Perspective in Aboriginal American Culture: A Study in Method. Geological Survey of Canada, Memoir 90.",
}
# family, glottolog node, hypothesis, place, lat, lon, years ago low, high, date in words, note, refs
H = [
    ("Indo-European", "indo1319", "Steppe hypothesis", "Pontic-Caspian steppe, north of the Black and Caspian seas", 48.0, 40.0, 4500, 6500,
     "roughly 4,500 to 6,500 years ago (Anthony's c. 4500 to 2500 BCE)", "The majority view among linguists and archaeologists, strengthened by ancient DNA showing a large movement of steppe ancestry into Europe about 5,000 years ago.", "anthony2007;anthony2015;haak2015"),
    ("Indo-European", "indo1319", "Anatolian hypothesis", "Central Anatolia (modern Turkey)", 38.5, 33.0, 8000, 9500,
     "roughly 8,000 to 9,500 years ago, with the spread of farming (the authors' approximate range)", "Links the family's spread to the first farmers; supported by some dated phylogenies, rejected by most specialists because of shared vocabulary for wheels and wagons.", "renfrew1987;bouckaert2012"),
    ("Indo-European", "indo1319", "Hybrid hypothesis", "South of the Caucasus (northern Fertile Crescent)", 39.5, 44.5, 8100, 8100,
     "about 8,100 years ago for the first split (the authors' estimate)", "A dated phylogeny places the root south of the Caucasus, with a later branch moving onto the steppe.", "heggarty2023"),
    ("Austronesian", "aust1307", "Out of Taiwan", "Taiwan", 23.7, 120.9, 5000, 5500,
     "roughly 5,000 to 5,500 years ago", "Widely accepted: all but one of Austronesian's first-order branches are spoken only on Taiwan.", "blust1999;gray2009"),
    ("Bantu", "narr1281", "Grassfields origin", "Cameroon and Nigeria borderland (Grassfields)", 6.0, 10.3, 4000, 5000,
     "roughly 4,000 to 5,000 years ago", "Widely accepted. Bantu is one branch of Atlantic-Congo; the routes of the later spread south and east are debated.", "vansina1995;grollemund2015"),
    ("Uralic", "ural1272", "Volga-Kama", "Middle Volga, Kama and the Ural Mountains (approximate)", 56.5, 53.0, None, None,
     "no single agreed date; a dated phylogeny puts the family's first splits several thousand years ago", "One of two contested views: a homeland in the Volga and Kama region west of the Urals.", "honkola2013"),
    ("Uralic", "ural1272", "Western Siberia", "Western Siberia, the Sayan and upper Yenisei area (approximate)", 54.0, 90.0, 4200, None,
     "spread west from about 4,200 years ago", "The more recent of the two contested views: a homeland in Siberia, with a spread west to the Volga in the early Metal Age, roughly 4,200 to 3,900 years ago.", "grunthal2022;janhunen2009"),
    ("Turkic", "turk1311", "Eastern steppe", "Mongolia and southern Siberia", 48.5, 102.0, 1500, 2800,
     "about 2,100 years ago for the first split, Bolgar and Common Turkic (95% range 1,500 to 2,800)", "Broadly agreed for Proto-Turkic itself; its deeper ancestry and any link to Mongolic or other families are disputed.", "golden1992;savelyev2020"),
    ("Sino-Tibetan", "sino1245", "Yellow River", "Upper and middle Yellow River basin, northern China", 35.0, 107.0, 5900, 7200,
     "roughly 5,900 to 7,200 years ago (the two studies' estimates)", "Supported by two dated phylogenies; an alternative places the homeland further south-west, in Sichuan or north-east India.", "zhang2019;sagart2019"),
    ("Afro-Asiatic", "afro1255", "African origin", "Horn of Africa and the Red Sea hills", 13.0, 38.0, 10000, None,
     "more than 10,000 years ago, by Ehret's reckoning possibly much earlier", "Five of the six branches are spoken only in Africa; very old and very uncertain.", "ehret1995;ehret2004"),
    ("Afro-Asiatic", "afro1255", "Levantine origin", "The Levant", 32.5, 35.5, 10000, None,
     "more than 10,000 years ago, linked by Militarev to the Natufian", "Rests on reconstructed farming words; a minority view.", "militarev2002"),
    ("Niger-Congo", "atla1278", "West African origin", "West Africa, perhaps the inland Niger region", 11.0, -3.0, 10000, None,
     "probably more than 10,000 years ago; no agreed date", "The most uncertain of all: Glottolog does not accept Niger-Congo as a proven family and lists Atlantic-Congo, Mande, Dogon, Ijoid and others separately.", "williamson2000;guldemann2018"),
    ("Pama-Nyungan", "pama1250", "Gulf Plains", "Gulf Plains of north-west Queensland, Australia", -18.5, 141.0, 5500, 6500,
     "roughly 6,000 years ago (the authors' approximate estimate)", "From a dated phylogeography of the family; Pama-Nyungan covers most of Australia.", "bouckaert2018"),
    ("Uto-Aztecan", "utoa1244", "Southern origin", "Northern and central Mexico", 22.5, -103.0, 4000, 5000,
     "roughly 4,000 to 5,000 years ago", "Argues that Proto-Uto-Aztecan speakers were maize farmers who spread north.", "hill2001"),
    ("Uto-Aztecan", "utoa1244", "Northern origin", "South-western United States, southern Great Basin", 35.0, -114.5, 4000, 5000,
     "roughly 4,000 to 5,000 years ago", "Argues from plant and animal names for a homeland of foragers in the south-west United States.", "fowler1983"),
    ("Quechuan", "quec1387", "Central Peru", "Central coast and highlands of Peru", -12.0, -76.5, 1500, 2500,
     "roughly 1,500 to 2,500 years ago", "Broadly agreed: the deepest split, between Quechua I and II, lies in central Peru, far from the later Inca centre at Cusco.", "torero1964;adelaar2004"),
]
for h in H:
    for r in h[10].split(";"):
        assert r in REFS, r
    assert h[1] in N, h[1]
with open(f"{DATA}/homelands_literature.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["family", "glottolog_node", "hypothesis", "place", "latitude", "longitude", "years_ago_low", "years_ago_high",
                "date", "note", "reference_keys", "references"])
    for h in H:
        w.writerow(list(h[:6]) + [h[6] if h[6] else "", h[7] if h[7] else ""] + list(h[8:11]) + [" | ".join(REFS[k] for k in h[10].split(";"))])

# ------------------------------------------------------------------ 2. computed centres
R_KM = 500


def unit(lat, lon):
    a, b = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a)])


def smean(lats, lons, w=None):
    v = unit(np.asarray(lats, float), np.asarray(lons, float))
    m = (v * (np.ones(len(v)) if w is None else np.asarray(w, float))[:, None]).sum(0)
    m /= np.linalg.norm(m)
    return float(np.degrees(np.arcsin(m[2]))), float(np.degrees(np.arctan2(m[1], m[0])))


def deep_branches(members, node):
    """members: languages under node. Returns {branch id: [languages]}."""
    def split(ms, nd):
        depth = len(N[nd]["path"]) if "path" in N[nd] else None
        out = defaultdict(list)
        for l in ms:
            p = l["path"]
            k = p.index(nd)
            b = p[k + 1] if k + 1 < len(p) else l["id"]
            out[b].append(l)
        return {b: v for b, v in out.items() if not (b in N and N[b]["name"].startswith("Unclassified"))}
    br = split(members, node)
    while len(br) <= 2 and br:
        big = max(br, key=lambda b: len(br[b]))
        if len(br[big]) < .8 * sum(len(v) for v in br.values()) or big not in N:
            break
        sub = split(br[big], big)
        if len(sub) < 2:
            break
        del br[big]; br.update(sub)
    return br


def centres(node, members):
    living = [l for l in members if l["aes"] != 6] or members
    clat, clon = smean([l["lat"] for l in living], [l["lon"] for l in living])
    br = deep_branches(members, node)
    out = {"node": node, "name": N[node]["name"], "n": len(members), "n_living": sum(1 for l in members if l["aes"] != 6),
           "centre": [round(clat, 3), round(clon, 3)], "n_branches": len(br)}
    if len(br) >= 2:
        bc = {b: smean([l["lat"] for l in v], [l["lon"] for l in v]) for b, v in br.items()}
        blat, blon = smean([c[0] for c in bc.values()], [c[1] for c in bc.values()])
        lab = {}
        for b, v in br.items():
            for l in v:
                lab[l["id"]] = b
        ms = [l for l in members if l["id"] in lab]
        U = unit([l["lat"] for l in ms], [l["lon"] for l in ms])
        cosr = math.cos(R_KM / 6371.0)
        best = None
        for i, l in enumerate(ms):
            near = (U @ U[i]) >= cosr
            nb = len({lab[ms[j]["id"]] for j in np.nonzero(near)[0]})
            key = (nb, int(near.sum()), -great_circle_km(l["lat"], l["lon"], blat, blon))
            if best is None or key > best[0]:
                best = (key, l)
        out.update({"hotspot": [round(best[1]["lat"], 3), round(best[1]["lon"], 3)], "hotspot_lang": best[1]["name"],
                    "hotspot_branches": best[0][0], "branch_centre": [round(blat, 3), round(blon, 3)],
                    "branches": sorted([N[b]["name"] if b in N else next(l["name"] for l in L if l["id"] == b) for b in br])})
    return out


fam = defaultdict(list)
for l in SP:
    if l["top"]:
        fam[l["top"]].append(l)
C = {}
for f_, ms in fam.items():
    C[f_] = centres(f_, ms)
bantu = [l for l in SP if "narr1281" in l["path"]]
C["narr1281"] = centres("narr1281", bantu)
# distances from the computed points to each proposed homeland
for h in H:
    c = C.get(h[1])
    if not c:
        continue
    c.setdefault("homeland_km", {})[h[2]] = {k: round(great_circle_km(h[4], h[5], *c[k])) for k in ("centre", "hotspot", "branch_centre") if k in c}
jsave(C, f"{WORK}/centres.json")
with open(f"{DATA}/family_centres.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["glottocode", "family", "n_spoken_languages", "n_living", "present_centre_lat", "present_centre_lon", "n_deep_branches",
                "hotspot_lat", "hotspot_lon", "hotspot_language", "deep_branches_within_500km", "branch_centre_lat", "branch_centre_lon", "deep_branches"])
    for k, c in sorted(C.items(), key=lambda kv: -kv[1]["n"]):
        w.writerow([k, c["name"], c["n"], c["n_living"], *c["centre"], c["n_branches"], *(c.get("hotspot") or ["", ""]), c.get("hotspot_lang", ""),
                    c.get("hotspot_branches", ""), *(c.get("branch_centre") or ["", ""]), "; ".join(c.get("branches", []))])
jsave({"H": [dict(zip(["family", "node", "hyp", "place", "lat", "lon", "lo", "hi", "date", "note", "refs"], h)) for h in H], "REFS": REFS}, f"{WORK}/homelands.json")
for h in H:
    c = C[h[1]]
    print(f"{h[0]:14s} {h[2]:22s} centre {c['centre']} hotspot {c.get('hotspot')} ({c.get('hotspot_lang')}, {c.get('hotspot_branches')}/{c['n_branches']}) km {c['homeland_km'][h[2]]}")
