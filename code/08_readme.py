"""README.md and LICENSE. Numbers come from data/results.json."""
import checks  # noqa: F401
from common import *

R = jload(f"{DATA}/results.json")
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
README = """# Where languages come from: the world's language families, their proposed homelands and where they are spoken today

An interactive map and data study of every language in Glottolog {{meta.glottolog|raw}}: {{counts.spoken|int}} spoken languages in {{counts.families|int}} families and {{counts.isolates|int}} isolates, with a family tree you can browse from Indo-European down to English, endangerment, Wikidata speaker counts, diversity per area, and a clearly labelled layer of published homeland hypotheses for eleven large families beside centres computed from Glottolog.

Interactive page: https://maps.tristanhotham.com/language-origins/
Paper: https://doi.org/{{DOI}}
Blog post: https://blog.tristanhotham.com/2026/10/31/language-origins/

## Headline results

- Glottolog's {{counts.spoken|int}} spoken first languages belong to {{counts.lineages|int}} lineages: {{counts.families|int}} families and {{counts.isolates|int}} isolates. {{counts.lineages_living|int}} lineages still have a living language. Five families (Atlantic-Congo, Austronesian, Indo-European, Sino-Tibetan, Afro-Asiatic) hold {{counts.top5_share|pc1}} of all languages; {{counts.families_le5|int}} families have five or fewer.
- Endangerment (Glottolog AES): {{aes.safe_pct|pc1}} not endangered, {{aes.endangered_pct|pc1}} endangered (threatened to nearly extinct), {{aes.extinct_pct|pc1}} extinct. In the Australia macroarea {{macro_by.Australia.extinct_pct|pc1}} are extinct, in South America {{macro_by.South America.extinct_pct|pc1}}, in North America {{macro_by.North America.extinct_pct|pc1}}.
- Diversity: Papua New Guinea has {{countries.png_n|int}} living languages from {{countries.png_lineages|int}} lineages; Vanuatu has {{countries.top_density.0.per10k|f1}} per 10,000 km². The densest 1% of land ({{grid.top1pct_cells|int}} squares of {{grid.cell_km|int}} km) holds {{grid.top1pct_share|pc1}} of living languages; the densest square, in {{grid.top_n.0.place|raw}}, has {{grid.top_n.0.n|int}}.
- Speakers (Wikidata, {{speakers.n|int}} languages, {{speakers.coverage_pct|pc1}} coverage, mixed years and definitions): the 10 largest languages account for {{speakers.top10_share|pc1}} of all speakers counted, the 20 largest for {{speakers.top20_share|pc1}}; the median language with a count has {{speakers.median|int}} speakers.
- Origins: the hotspot where a family's deepest branches crowd together lies within 500 km of a proposed homeland for {{origins.n_hot_within500|int}} of {{origins.n_compared|int}} families (Austronesian, Bantu, Pama-Nyungan, Quechuan, northern Uto-Aztecan), but more than 1,000 km from all three Indo-European proposals.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; it loads `data/langs.json`, `data/tree.json`, `data/grid.json` and `data/dialects.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/languages.csv` | Every mapped language (no bookkeeping entries): glottocode, name, ISO 639-3, coordinates, macroarea, countries, category, family, classification path (codes and names), endangerment, most extensive description, dialects, Wikidata speaker count and year ({{SIZE_LANG}}). |
| `data/families.csv` | Each top-level family: languages, living, endangered, extinct, Wikidata speakers, present centre, diversity hotspot, map colour. |
| `data/family_centres.csv` | Present centre, diversity hotspot and branch centre for every family and for Bantu, with the deep branches used. |
| `data/homelands_literature.csv` | The {{origins.n_hyp|int}} homeland hypotheses: family, hypothesis, place, approximate coordinates, date range, note and full references. |
| `data/countries.csv` | Living languages, lineages, families, isolates and density per country. |
| `data/diversity_grid.csv` | Living and all languages and lineages per {{grid.cell_km|int}} km equal-area square. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/langs.json`, `data/tree.json`, `data/grid.json`, `data/dialects.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data. |
| `code/` | Numbered scripts (run in order), page, paper and blog templates, `checks.py` (asserts for every fact stated in words) and `qa.js` (browser checks). |
| `release/` | Paper PDF and LaTeX source with figures, blog post with figures and meta, Zenodo files and metadata. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Languages: Glottolog language-level entries, minus {{counts.bookkeeping|int}} 'bookkeeping' entries. Families, endangerment, diversity and speakers use the {{counts.spoken|int}} spoken first languages; sign languages, pidgins, unclassifiable, unattested, artificial and mixed languages are mapped but not in families. Lineage = top-level family or isolate. Living = any status but extinct.
- Endangerment: Glottolog's Agglomerated Endangerment Status; threatened, shifting, moribund and nearly extinct count as endangered.
- Diversity: Glottolog's country lists, and an equal-area grid of {{grid.cell_km|int}} km squares (Equal Earth projection) on Natural Earth land.
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

- Hammarström, H., Forkel, R., Haspelmath, M. and Bank, S. (2025) Glottolog {{meta.glottolog|raw}}. Leipzig: Max Planck Institute for Evolutionary Anthropology. https://glottolog.org (CLDF release). CC BY 4.0.
- Wikidata, number of speakers (P1098) and Glottolog codes (P1394). CC0.
- Natural Earth countries, land, admin-1 regions and populated places. Public domain.
- Homeland hypotheses: the published studies listed with full references in `data/homelands_literature.csv` and the paper.
- Base map tiles on the page: © Esri.

Code: MIT. Text, figures and derived data: CC BY 4.0 (derived from Glottolog, CC BY 4.0, and Wikidata, CC0).

## Citation

Hotham, T. (2026) Where languages come from: the world's language families, their proposed homelands and where they are spoken today. Zenodo. https://doi.org/{{DOI}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
"""
txt = placeholders(fill(README.replace("{{SIZE_LANG}}", size("languages.csv")), R))
for bad in ("—", "–", "--"):
    assert bad not in txt.replace("|---|---|", ""), bad   # the table rule is markdown syntax, not text
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(txt)
LIC = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data

Text, figures and derived data in this repository are licensed under the Creative Commons Attribution 4.0 International
licence (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. They include data derived from Glottolog
(Hammarström, Forkel, Haspelmath and Bank, Max Planck Institute for Evolutionary Anthropology, CC BY 4.0) and Wikidata (CC0).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(LIC)
print("README", len(txt.split()), "words")
