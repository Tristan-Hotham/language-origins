# Where languages come from: the world's language families, their proposed homelands and where they are spoken today

An interactive map and data study of every language in Glottolog 5.2.1: 7,674 spoken languages in 238 families and 183 isolates, with a family tree you can browse from Indo-European down to English, endangerment, Wikidata speaker counts, diversity per area, and a clearly labelled layer of published homeland hypotheses for eleven large families beside centres computed from Glottolog.

Interactive page: https://maps.tristanhotham.com/language-origins/
Paper: https://doi.org/10.5281/zenodo.23844509
Blog post: https://blog.tristanhotham.com/2026/10/31/language-origins/

## Headline results

- Glottolog's 7,674 spoken first languages belong to 421 lineages: 238 families and 183 isolates. 314 lineages still have a living language. Five families (Atlantic-Congo, Austronesian, Indo-European, Sino-Tibetan, Afro-Asiatic) hold 54.3% of all languages; 135 families have five or fewer.
- Endangerment (Glottolog AES): 35.0% not endangered, 52.1% endangered (threatened to nearly extinct), 12.8% extinct. In the Australia macroarea 63.9% are extinct, in South America 35.1%, in North America 28.2%.
- Diversity: Papua New Guinea has 850 living languages from 77 lineages; Vanuatu has 102.2 per 10,000 km². The densest 1% of land (45 squares of 200 km) holds 27.6% of living languages; the densest square, in Madang, Papua New Guinea, has 148.
- Speakers (Wikidata, 1,627 languages, 21.2% coverage, mixed years and definitions): the 10 largest languages account for 50.9% of all speakers counted, the 20 largest for 62.6%; the median language with a count has 20,000 speakers.
- Origins: the hotspot where a family's deepest branches crowd together lies within 500 km of a proposed homeland for 5 of 11 families (Austronesian, Bantu, Pama-Nyungan, Quechuan, northern Uto-Aztecan), but more than 1,000 km from all three Indo-European proposals.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; it loads `data/langs.json`, `data/tree.json`, `data/grid.json` and `data/dialects.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/languages.csv` | Every mapped language (no bookkeeping entries): glottocode, name, ISO 639-3, coordinates, macroarea, countries, category, family, classification path (codes and names), endangerment, most extensive description, dialects, Wikidata speaker count and year (2.3 MB). |
| `data/families.csv` | Each top-level family: languages, living, endangered, extinct, Wikidata speakers, present centre, diversity hotspot, map colour. |
| `data/family_centres.csv` | Present centre, diversity hotspot and branch centre for every family and for Bantu, with the deep branches used. |
| `data/homelands_literature.csv` | The 16 homeland hypotheses: family, hypothesis, place, approximate coordinates, date range, note and full references. |
| `data/countries.csv` | Living languages, lineages, families, isolates and density per country. |
| `data/diversity_grid.csv` | Living and all languages and lineages per 200 km equal-area square. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/langs.json`, `data/tree.json`, `data/grid.json`, `data/dialects.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data. |
| `code/` | Numbered scripts (run in order), page, paper and blog templates, `checks.py` (asserts for every fact stated in words) and `qa.js` (browser checks). |
| `release/` | Paper PDF and LaTeX source with figures, blog post with figures and meta, Zenodo files and metadata. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Languages: Glottolog language-level entries, minus 380 'bookkeeping' entries. Families, endangerment, diversity and speakers use the 7,674 spoken first languages; sign languages, pidgins, unclassifiable, unattested, artificial and mixed languages are mapped but not in families. Lineage = top-level family or isolate. Living = any status but extinct.
- Endangerment: Glottolog's Agglomerated Endangerment Status; threatened, shifting, moribund and nearly extinct count as endangered.
- Diversity: Glottolog's country lists, and an equal-area grid of 200 km squares (Equal Earth projection) on Natural Earth land.
- Speakers: Wikidata 'number of speakers' for items with a Glottolog code. The most recent dated count; if several share that date, the smallest (usually first-language); if none is dated, the largest; dates before 1800 treated as errors.
- Origins: homelands typed in from the cited literature (approximate regional centres and the authors' dates). Present centre = spherical mean of living languages. Diversity hotspot = the language with the most distinct deep branches within 500 km (deep branches = top-level subgroups, split further where one holds 80% or more and there are no more than two).
- Caveats: the language/dialect line is a judgement; one dot per language shows where languages come from, not where speakers live now; speaker counts are patchy and mixed; homelands are contested hypotheses and the computed points are heuristics.

## How to rerun

Needs Python 3 with pandas, numpy, shapely, pyproj, matplotlib, fontTools and Pillow; xelatex (TeX Gyre Pagella, Inter) and pdftotext; node with Playwright and Leaflet 1.9.4 for `qa.js`. Raw inputs, retrieved in 2026, are read in place from the paths in `code/common.py` (Glottolog CLDF folder, Wikidata TSV, Natural Earth GeoJSON). Intermediate files go to `/dev/shm/langorig/work` (set `LANGTMP` to change). Set `STUDY_DOI` and `STUDY_BLOG_URL` to fill the placeholders.

```
python3 code/01_glottolog.py    # Glottolog and Wikidata into one language table and the family tree
python3 code/02_geo.py          # outlines, place names, country areas, equal-area grid
python3 code/03_origins.py      # homelands from the literature, computed centres and hotspots
python3 code/04_results.py      # results.json and page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/08_readme.py       # README and LICENSE
python3 code/09_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
node code/qa.js                 # screenshots and console check
```

## Sources and licences

- Hammarström, H., Forkel, R., Haspelmath, M. and Bank, S. (2025) Glottolog 5.2.1. Leipzig: Max Planck Institute for Evolutionary Anthropology. https://glottolog.org (CLDF release). CC BY 4.0.
- Wikidata, number of speakers (P1098) and Glottolog codes (P1394). CC0.
- Natural Earth countries, land, admin-1 regions and populated places. Public domain.
- Homeland hypotheses: the published studies listed with full references in `data/homelands_literature.csv` and the paper.
- Base map tiles on the page: © Esri.

Code: MIT. Text, figures and derived data: CC BY 4.0 (derived from Glottolog, CC BY 4.0, and Wikidata, CC0).

## Citation

Hotham, T. (2026) Where languages come from: the world's language families, their proposed homelands and where they are spoken today. Zenodo. https://doi.org/10.5281/zenodo.23844509

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
