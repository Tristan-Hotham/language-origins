"""r/dataisbeautiful collage for language-origins: 2400 x 3000 px, light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
import checks  # noqa: F401
from matplotlib.lines import Line2D

R = jload(f"{DATA}/results.json")
c, a, sp = R["counts"], R["aes"], R["speakers"]
BGC = "#F8F5EE"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGC)
fig.text(.045, .972, "Where languages come from", fontproperties=DISP, fontsize=56, color=FG, va="top")
fig.text(.045, .905, f"Every one of the world's {c['spoken']:,} spoken languages in Glottolog, at its home location, coloured by family.\n"
         f"They belong to {c['families']} families and {c['isolates']} isolates: {c['lineages']} lineages with no proven link between them.",
         fontproperties=SERP, fontsize=15.5, color=FG, va="top", linespacing=1.45)

ax = fig.add_axes([0, .535, 1, .31]); ax.set_facecolor(BGC)
world(ax, fc=LAND, ec=BGC, lw=.4, extent=(-12.4e6, 15.9e6, -5.7e6, 8.0e6))
lang_points(ax, s=5.5, only=lambda l: l[4] >= -1)


def note(lon, lat, text, ha="left"):
    x, y = tr.transform(lon, lat)
    ax.text(x, y, text, fontsize=10.5, color=FG, family=MONO, ha=ha, va="top", zorder=6, linespacing=1.35)


# notes on open sea only
note(55, -30, f"Papua New Guinea:\n{R['countries']['png_n']} living languages\nfrom {R['countries']['png_lineages']} lineages", "left")
note(-46, -26, "One dot per language:\nEnglish is a single\ndot, in England", "left")
note(60, -14, f"Australia: {R['macro_by']['Australia']['extinct_pct']:.0f}% of\nlanguages extinct", "left")

p = SERP.copy(); p.set_size(11.5)
LEG = SITE["legend"]
h = [Line2D([], [], marker="o", ls="", ms=8, mfc=FCOL[FIDX[k]], mec="none", label=FAM[FIDX[k]][1]) for k in LEG[:22]]
h += [Line2D([], [], marker="o", ls="", ms=8, mfc="#A79C8C", mec="none", label="Other families (muted tones)"),
      Line2D([], [], marker="o", ls="", ms=8, mfc=SITE["iso_col"], mec="none", label="Isolates")]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(.035, .53), ncol=4, frameon=False, prop=p, handletextpad=.3, columnspacing=1.2, labelspacing=.45)

# big numbers
nums = [(f"{c['lineages']}", HOT, f"separate lineages:\n{c['families']} families and\n{c['isolates']} isolates"),
        (f"{a['endangered_pct']:.1f}%", GOLD, f"of spoken languages\nare endangered; a\nfurther {a['extinct_pct']:.1f}% extinct"),
        (f"{a['safe_pct']:.1f}%", "#3E8E6E", "are rated not\nendangered"),
        (f"{sp['top20_share']:.1f}%", "#C8323C", f"of all speakers counted\nspeak one of the 20\nlargest languages")]
for i, (big, col, sub) in enumerate(nums):
    x = .045 + i * .235
    fig.text(x, .405, big, fontproperties=DISP, fontsize=40, color=col, va="top")
    fig.text(x, .352, sub, family=MONO, fontsize=11.5, color=FG, va="top", linespacing=1.5)

# panel 1: endangerment by region
K = [1, 2, 3, 4, 5, 6]
a1 = fig.add_axes([.14, .09, .23, .115]); a1.set_facecolor(BGC)
ms = R["macro"]
for i, m in enumerate(ms):
    left = 0
    for j, k in enumerate(K):
        v = 100 * m["counts"][j] / m["n"]
        a1.barh(len(ms) - 1 - i, v, left=left, color=AESC[k], height=.72); left += v
a1.set_yticks(range(len(ms))[::-1]); a1.set_yticklabels([m["name"] for m in ms], fontsize=10)
a1.set_xlim(0, 100); a1.set_xticks([0, 50, 100]); a1.set_xticklabels(["0%", "50%", "100%"], fontsize=9.5)
for s_ in ("top", "right", "left"): a1.spines[s_].set_visible(False)
a1.tick_params(axis="y", length=0)
fig.text(.03, .262, "Endangerment by region", family=MONO, fontsize=13, color=FG, fontweight="medium")
fig.legend(handles=[Line2D([], [], marker="s", ls="", ms=8, mfc=AESC[k], mec="none", label=AESN[k]) for k in K], loc="upper left",
           bbox_to_anchor=(.025, .255), ncol=3, frameon=False, prop={"family": MONO, "size": 9}, handletextpad=.2, columnspacing=.8)

# panel 2: largest families
a2 = fig.add_axes([.555, .085, .12, .155]); a2.set_facecolor(BGC)
tf = R["top_families"][:8]
yy = np.arange(len(tf))[::-1]
a2.barh(yy, [f["n"] for f in tf], color=[FCOL[FIDX[f["id"]]] for f in tf], height=.72)
a2.set_yticks(yy); a2.set_yticklabels([f["name"].replace("Nuclear Trans New Guinea", "Trans New Guinea") for f in tf], fontsize=9.5)
for y_, f in zip(yy, tf):
    a2.text(f["n"] + 30, y_, f"{f['n']:,}", va="center", fontsize=9, color=MUT)
a2.set_xlim(0, 1800); a2.set_xticks([])
for s_ in ("top", "right", "left", "bottom"): a2.spines[s_].set_visible(False)
a2.tick_params(axis="y", length=0)
fig.text(.40, .262, "Largest families", family=MONO, fontsize=13, color=FG, fontweight="medium")

# panel 3: speaker concentration
allc = sorted([l[6] for l in LG if l[6] and l[4] != -2], reverse=True)
cum = np.cumsum(allc) / sum(allc) * 100
a3 = fig.add_axes([.77, .1, .19, .135]); a3.set_facecolor(BGC)
a3.plot(np.arange(1, len(cum) + 1), cum, color=HOT, lw=2)
a3.set_xscale("log"); a3.set_xlim(1, len(cum)); a3.set_ylim(0, 102)
a3.set_xticks([1, 10, 100, 1000]); a3.set_xticklabels(["1", "10", "100", "1,000"], fontsize=9.5)
a3.set_yticks([0, 50, 100]); a3.set_yticklabels(["0%", "50%", "100%"], fontsize=9.5)
for n_, v in ((10, sp["top10_share"]), (20, sp["top20_share"])):
    a3.plot([n_], [v], "o", color=GOLD, ms=5)
a3.text(13, sp["top10_share"] - 4, f"top 10: {sp['top10_share']:.0f}%", fontsize=9.5, va="top")
a3.text(26, sp["top20_share"] - 4, f"top 20: {sp['top20_share']:.0f}%", fontsize=9.5, va="top")
for s_ in ("top", "right"): a3.spines[s_].set_visible(False)
a3.set_xlabel("languages, largest first", fontsize=9.5)
fig.text(.72, .262, "Speakers counted", family=MONO, fontsize=13, color=FG, fontweight="medium")
fig.text(.72, .25, f"Wikidata counts, {sp['n']:,} languages", family=MONO, fontsize=9.5, color=MUT)

fig.text(.045, .022, f"Sources: Glottolog {GLOTTOLOG_VERSION} (Hammarström, Forkel, Haspelmath and Bank; CC BY 4.0); Wikidata speaker counts (CC0, mixed years); Natural Earth.\n"
         "Endangerment: Glottolog's Agglomerated Endangerment Status. Analysis and chart: Tristan Hotham  ·  maps.tristanhotham.com/language-origins",
         family=MONO, fontsize=9.5, color=MUT, va="bottom", linespacing=1.6)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "where_languages_come_from.png")
fig.savefig(out, dpi=200, facecolor=BGC); plt.close(fig)
from PIL import Image
print(Image.open(out).size)

# numbers quoted in post.md, checked against results.json
post = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.md"), encoding="utf-8").read()
for v in (f"{c['spoken']:,}", f"{c['lineages']} separate", f"{a['endangered_pct']:.1f}%", f"{c['families']} families", f"{c['isolates']} isolates",
          f"{c['top5_share']:.1f}%", f"{a['safe_pct']:.1f}%", f"{a['extinct_pct']:.1f}%", f"{R['macro_by']['Australia']['extinct_pct']:.0f}% in Australia",
          f"{R['countries']['png_n']} living languages from {R['countries']['png_lineages']} lineages", f"{sp['n']:,} languages", f"{sp['top20_share']:.1f}%", GLOTTOLOG_VERSION):
    assert v in post, v
for bad in ("—", "–", "--"):
    assert bad not in post
print("post.md checked")
