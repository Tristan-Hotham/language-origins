"""Static figures: header card (header.png), paper figures (release/paper/f_*.png) and blog figures (release/blog/b_*.png).
All numbers come from data/results.json; maps use the Equal Earth projection."""
import csv
from matplotlib.patches import Patch, Rectangle, Polygon as MPoly
from matplotlib.lines import Line2D
import checks  # noqa: F401
from figstyle import *

R = jload(f"{DATA}/results.json")
TREE = jload(f"{DATA}/tree.json")["N"]
GRID = jload(f"{DATA}/grid.json")
PAP = os.path.join(ROOT, "release", "paper"); BLOGD = os.path.join(ROOT, "release", "blog")
os.makedirs(PAP, exist_ok=True); os.makedirs(BLOGD, exist_ok=True)
NIDX = {n[0]: j for j, n in enumerate(TREE)}
LEG = SITE["legend"]


def both(fig, name):
    fig.savefig(f"{PAP}/f_{name}.png", dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(f"{BLOGD}/b_{name}.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def fam_legend(fig, y, ncol=5, size=10.5, x=.04, n=20):
    p = SERP.copy(); p.set_size(size)
    h = [Line2D([], [], marker="o", ls="", ms=7, mfc=FCOL[FIDX[k]], mec="none", label=FAM[FIDX[k]][1]) for k in LEG[:n]]
    h += [Line2D([], [], marker="o", ls="", ms=7, mfc="#A79C8C", mec="none", label="Other families (muted tones)"),
          Line2D([], [], marker="o", ls="", ms=7, mfc=SITE["iso_col"], mec="none", label="Isolates")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(x, y), ncol=ncol, frameon=False, prop=p, handletextpad=.3, columnspacing=1.1, labelspacing=.45)


# ---------------------------------------------------------------- 1. families map
fig = plt.figure(figsize=(12, 7.6), facecolor=BG)
ax = fig.add_axes([0, .26, 1, .74]); ax.set_facecolor(BG)
world(ax, fc=LAND, ec=BG, lw=.4)
lang_points(ax, s=4.2, only=lambda l: l[4] >= -1)
lang_points(ax, s=4, colour=lambda l: "#FFFFFF", ec="#8d8679", lw=.5, only=lambda l: l[4] == -2, zorder=2)
fam_legend(fig, .255, ncol=4, size=11)
both(fig, "families_map")

# ---------------------------------------------------------------- 2. families bar
fams = R["top_families"]
fig, ax = plt.subplots(figsize=(9, 5.4), facecolor=BG); ax.set_facecolor(BG)
y = np.arange(len(fams))[::-1]
ax.barh(y, [f["n"] for f in fams], color=[mix(FCOL[FIDX[f["id"]]], "#FFFFFF", .55) for f in fams], height=.72)
ax.barh(y, [f["living"] for f in fams], color=[FCOL[FIDX[f["id"]]] for f in fams], height=.72)
for yy, f in zip(y, fams):
    ax.text(f["n"] + 15, yy, f"{f['n']:,}", va="center", fontsize=9.5, color=MUT)
ax.set_yticks(y); ax.set_yticklabels([f["name"] for f in fams], fontproperties=SERP, fontsize=11)
for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
ax.tick_params(axis="y", length=0); ax.set_xlabel("Spoken languages in Glottolog (pale: extinct)", fontsize=10)
ax.set_xlim(0, fams[0]["n"] * 1.1)
fig.tight_layout(); fig.savefig(f"{PAP}/f_families.png", dpi=200, facecolor=BG); plt.close(fig)

# ---------------------------------------------------------------- 3. Indo-European by deep branch
ie = NIDX["indo1319"]; cie = NIDX["clas1257"]
kids = [j for j, n in enumerate(TREE) if n[2] in (ie, cie) and j != cie and not n[1].startswith("Unclassified")]
kids.sort(key=lambda j: -TREE[j][3])
BRC = ["#3557B0", "#E07B27", "#2E9E6E", "#C8323C", "#7B4BA8", "#C99A18", "#1C9AA8", "#B0407A", "#6FAE3A", "#8C5A2E", "#5BA4D9"]
kc = {k: BRC[i] for i, k in enumerate(kids)}
fig = plt.figure(figsize=(12, 7.2), facecolor=BG)
ax = fig.add_axes([0, .14, 1, .86]); ax.set_facecolor(BG)
ext = (*tr.transform(-24, 30)[:1], *tr.transform(104, 30)[:1], tr.transform(0, 5)[1], tr.transform(0, 71)[1])
world(ax, fc=LAND, ec=BG, lw=.5, extent=ext)


def iecol(l):
    hit = next((x for x in l[9] if x in kc), None)
    return kc[hit] if hit is not None else ("#857f74" if ie in l[9] else None)


lang_points(ax, s=11, colour=iecol, ec="#FFFFFF", lw=.3)
p = SERP.copy(); p.set_size(11.5)
h = [Line2D([], [], marker="o", ls="", ms=8, mfc=kc[k], mec="none", label=f"{TREE[k][1]} ({TREE[k][3]})") for k in kids]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(.03, .135), ncol=4, frameon=False, prop=p, columnspacing=1.2)
both(fig, "ie_branches")

# ---------------------------------------------------------------- 4. diversity map (equal-area squares)
BINS = [1, 3, 6, 10, 20, 35, 60, 100]


def gcol(v, bins=BINS, lo="#CFE3E6", hi="#0B3F57"):
    i = max(j for j, b in enumerate(bins) if v >= b)
    return mix(lo, hi, i / (len(bins) - 1))


def grid_map(ax, key=1, bins=BINS, lo="#CFE3E6", hi="#0B3F57"):
    km = GRID["km"] * 1000
    for c in sorted(GRID["c"], key=lambda c: c[key]):
        if not c[key]:
            continue
        i, j = map(int, c[0].split(","))
        ax.add_patch(Rectangle((i * km, j * km), km, km, fc=gcol(c[key], bins, lo, hi), ec="none", zorder=2))


fig = plt.figure(figsize=(12, 7), facecolor=BG)
ax = fig.add_axes([0, .1, 1, .9]); ax.set_facecolor(BG)
world(ax, fc=LAND, ec=BG, lw=.4); grid_map(ax)
for iso, ps in SHAPES:
    for p_ in ps:
        ax.add_patch(MPoly(p_, closed=True, fc="none", ec="#FFFFFF", lw=.35, zorder=3))
hh = [Patch(fc=gcol(b), label=(f"{b} to {BINS[k + 1] - 1}" if k < len(BINS) - 1 and BINS[k + 1] - 1 > b else f"{b}" if k < len(BINS) - 1 else f"{b}+")) for k, b in enumerate(BINS)]
p = SERP.copy(); p.set_size(11)
fig.legend(handles=hh, loc="lower left", bbox_to_anchor=(.03, .01), ncol=8, frameon=False, prop=p, title=f"Living languages per {R['grid']['cell_km']} km square", title_fontsize=11, columnspacing=1)
both(fig, "diversity_map")

# ---------------------------------------------------------------- 5. countries
cs = R["countries"]["top_n"]
fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG); ax.set_facecolor(BG)
y = np.arange(len(cs))[::-1]
ax.barh(y, [c["n"] for c in cs], color=HOT, height=.7)
for yy, c in zip(y, cs):
    ax.text(c["n"] + 8, yy, f"{c['n']:,}", va="center", fontsize=9.5, color=MUT)
    ax.text(1000, yy, f"{c['lineages']}", va="center", ha="right", fontsize=10, color=GOLD, fontweight="medium")
ax.text(1000, len(cs) - .3, "lineages", ha="right", fontsize=9.5, color=MUT)
ax.set_yticks(y); ax.set_yticklabels([c["name"].replace("United States of America", "United States").replace("Dem. Rep. Congo", "DR Congo") for c in cs], fontproperties=SERP, fontsize=11)
for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
ax.tick_params(axis="y", length=0); ax.set_xlim(0, 1010); ax.set_xlabel("Living spoken languages listed in the country", fontsize=10)
fig.tight_layout(); fig.savefig(f"{PAP}/f_countries.png", dpi=200, facecolor=BG); plt.close(fig)

# ---------------------------------------------------------------- 6. endangerment by macroarea
K = [1, 2, 3, 4, 5, 6, 0]
fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
ms = R["macro"]
for i, m in enumerate(ms):
    left = 0
    for j, k in enumerate(K):
        v = 100 * m["counts"][j] / m["n"]
        ax.barh(len(ms) - 1 - i, v, left=left, color=AESC[k], height=.72)
        if v >= 7 and k:
            ax.text(left + v / 2, len(ms) - 1 - i, f"{v:.0f}%", ha="center", va="center", fontsize=9.5, color="#FFFFFF" if k in (1, 4, 5, 6) else FG)
        left += v
ax.set_yticks(range(len(ms))[::-1]); ax.set_yticklabels([f"{m['name']} ({m['n']:,})" for m in ms], fontproperties=SERP, fontsize=11)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
ax.tick_params(axis="y", length=0)
p = SERP.copy(); p.set_size(10.5)
fig.legend(handles=[Patch(fc=AESC[k], label=AESN[k]) for k in K[:6]], loc="lower center", ncol=6, frameon=False, prop=p, bbox_to_anchor=(.55, 0))
fig.tight_layout(rect=(0, .07, 1, 1)); both(fig, "aes_macro")

# ---------------------------------------------------------------- 7. endangerment map
fig = plt.figure(figsize=(12, 7), facecolor=BG)
ax = fig.add_axes([0, .1, 1, .9]); ax.set_facecolor(BG)
world(ax, fc=LAND, ec=BG, lw=.4)
order_ = sorted([l for l in LG if l[2] is not None and l[4] != -2], key=lambda l: {1: 0, 2: 1, 3: 2, 0: 3, 4: 4, 5: 5, 6: 6}[l[5]])
x, y = xy([l[2] for l in order_], [l[3] for l in order_])
ax.scatter(x, y, s=4.2, c=[AESC[l[5]] for l in order_], edgecolors="none", zorder=3)
fig.legend(handles=[Line2D([], [], marker="o", ls="", ms=7, mfc=AESC[k], mec="none", label=AESN[k]) for k in K[:6]], loc="lower left", bbox_to_anchor=(.03, .01), ncol=6, frameon=False, prop=p)
fig.savefig(f"{PAP}/f_aes_map.png", dpi=200, facecolor=BG); plt.close(fig)

# ---------------------------------------------------------------- 8. speakers
sp = R["speakers"]; top = sp["top"][:20]
allc = sorted([l[6] for l in LG if l[6] and l[4] != -2], reverse=True)
tot = sum(allc); cum = np.cumsum(allc) / tot * 100
fig = plt.figure(figsize=(12, 5.6), facecolor=BG)
a1 = fig.add_axes([.17, .1, .4, .82]); a1.set_facecolor(BG)
yy = np.arange(len(top))[::-1]
a1.barh(yy, [t["n"] / 1e6 for t in top], color=[FCOL[next(i for i, f in enumerate(FAM) if f[1] == t["family"])] for t in top], height=.72)
for y_, t in zip(yy, top):
    a1.text(t["n"] / 1e6 + 10, y_, f"{t['n'] / 1e6:,.0f}m" + (f" ({t['year']})" if t["year"] else ""), va="center", fontsize=8.5, color=MUT)
a1.set_yticks(yy); a1.set_yticklabels([t["name"] for t in top], fontproperties=SERP, fontsize=10.5)
for s_ in ("top", "right", "left"): a1.spines[s_].set_visible(False)
a1.tick_params(axis="y", length=0); a1.set_xlim(0, 1150); a1.set_xlabel("Speakers, millions (Wikidata)", fontsize=10)
a2 = fig.add_axes([.67, .14, .3, .74]); a2.set_facecolor(BG)
a2.plot(np.arange(1, len(cum) + 1), cum, color=HOT, lw=2.2)
a2.set_xscale("log"); a2.set_ylim(0, 102); a2.set_xlim(1, len(cum))
a2.set_xticks([1, 10, 100, 1000]); a2.set_xticklabels(["1", "10", "100", "1,000"])
for n_, v in ((10, sp["top10_share"]), (20, sp["top20_share"]), (100, sp["top100_share"])):
    a2.plot([n_], [v], "o", color=GOLD, ms=6, zorder=5)
    a2.text(n_ * 1.25, v - 6, f"top {n_}: {v:.1f}%", fontsize=9.5, color=FG)
a2.set_xlabel("Languages, largest first (log scale)", fontsize=10); a2.set_ylabel("Share of all speakers counted", fontsize=10)
a2.set_yticks([0, 25, 50, 75, 100]); a2.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
for s_ in ("top", "right"): a2.spines[s_].set_visible(False)
a2.set_title(f"{sp['n']:,} languages with a count", fontsize=10.5, color=MUT, loc="left")
both(fig, "speakers")

# ---------------------------------------------------------------- 9. origins map
H = SITE["homelands"]; CE = SITE["centres"]
OFF = {  # label offsets (km east, km north) and alignment, chosen by eye to keep labels on clear ground or sea
    ("Indo-European", "Steppe hypothesis"): (400, 350, "left"), ("Indo-European", "Anatolian hypothesis"): (-600, 700, "right"),
    ("Indo-European", "Hybrid hypothesis"): (400, -250, "left"), ("Austronesian", "Out of Taiwan"): (450, 100, "left"),
    ("Bantu", "Grassfields origin"): (-400, -650, "right"), ("Uralic", "Volga-Kama"): (-500, 550, "right"), ("Uralic", "Western Siberia"): (350, 450, "left"),
    ("Turkic", "Eastern steppe"): (400, 350, "left"), ("Sino-Tibetan", "Yellow River"): (400, 350, "left"),
    ("Afro-Asiatic", "African origin"): (450, -300, "left"), ("Afro-Asiatic", "Levantine origin"): (-700, -150, "right"),
    ("Niger-Congo", "West African origin"): (-450, 350, "right"), ("Pama-Nyungan", "Gulf Plains"): (-500, 650, "right"),
    ("Uto-Aztecan", "Southern origin"): (-500, -450, "right"), ("Uto-Aztecan", "Northern origin"): (400, 550, "left"),
    ("Quechuan", "Central Peru"): (-450, -200, "right")}


def origins_map(ax, labels=True, fs=9.5, ms=15):
    world(ax, fc=LAND, ec=BG, lw=.4)
    lang_points(ax, s=1.6, alpha=.35, only=lambda l: l[4] >= -1)
    done = set()
    for h in H:
        c = fam_col_node(h["node"])
        x, y = xy(h["lat"], h["lon"])
        ax.scatter([x], [y], marker=STARM, s=ms * 18, c=[c], edgecolors="#FFFFFF", linewidths=1.1, zorder=7)
        if labels:
            dx, dy, ha = OFF[(h["family"], h["hyp"])]
            multi = h["family"] in ("Indo-European", "Uralic", "Afro-Asiatic", "Uto-Aztecan")
            t = h["family"] + (": " + h["hyp"].replace(" hypothesis", "").replace(" origin", "") if multi else "")
            ax.annotate(t, (x, y), (x + dx * 1000, y + dy * 1000), fontsize=fs, ha=ha, va="center", color=FG, family=MONO, zorder=8,
                        arrowprops=dict(arrowstyle="-", color=MUT, lw=.6, shrinkA=1, shrinkB=5))
        if h["node"] in done:
            continue
        done.add(h["node"])
        ce = CE[h["node"]]
        cx, cy = xy(*ce["centre"])
        ax.scatter([cx], [cy], marker="o", s=ms * 4, facecolors="#FFFFFF", edgecolors=c, linewidths=2, zorder=6)
        if ce.get("hotspot"):
            hx, hy = xy(*ce["hotspot"])
            ax.scatter([hx], [hy], marker="D", s=ms * 3.2, c=[c], edgecolors="#FFFFFF", linewidths=1, zorder=6)


fig = plt.figure(figsize=(12, 7.2), facecolor=BG)
ax = fig.add_axes([0, .1, 1, .9]); ax.set_facecolor(BG)
origins_map(ax)
ax.set_xlim(-14.6e6, 15.4e6)
p = SERP.copy(); p.set_size(11)
fig.legend(handles=[Line2D([], [], marker=STARM, ls="", ms=13, mfc=GOLD, mec="#FFFFFF", label="Proposed homeland (literature)"),
                    Line2D([], [], marker="D", ls="", ms=7, mfc=GOLD, mec="#FFFFFF", label="Diversity hotspot (computed)"),
                    Line2D([], [], marker="o", ls="", ms=8, mfc="#FFFFFF", mec=GOLD, mew=2, label="Present centre (computed)")],
           loc="lower left", bbox_to_anchor=(.03, .01), ncol=3, frameon=False, prop=p)
both(fig, "origins_map")

# ---------------------------------------------------------------- 10. distances
rows = R["origins"]["rows"]
fig, ax = plt.subplots(figsize=(9.5, 5.8), facecolor=BG); ax.set_facecolor(BG)
for i, r in enumerate(rows):
    y_ = len(rows) - 1 - i; c = fam_col_node(r["node"])
    ax.plot([r["km_hotspot"], r["km_centre"]], [y_, y_], color=c, lw=2, alpha=.45)
    ax.scatter([r["km_centre"]], [y_], s=55, facecolors=BG, edgecolors=c, linewidths=2, zorder=3)
    ax.scatter([r["km_hotspot"]], [y_], s=60, c=[c], zorder=4)
ax.axvline(500, color=MUT, lw=1, ls=(0, (4, 3)))
ax.set_yticks(range(len(rows))[::-1]); ax.set_yticklabels([f"{r['family']}: {r['hyp'].replace(' hypothesis', '')}" for r in rows], fontproperties=SERP, fontsize=10.5)
ax.set_xlabel("Distance from the proposed homeland, km (dot: diversity hotspot; ring: present centre)", fontsize=10)
for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
ax.tick_params(axis="y", length=0); ax.set_xlim(0, 3600)
fig.tight_layout(); fig.savefig(f"{PAP}/f_origins_dist.png", dpi=200, facecolor=BG); plt.close(fig)

# ---------------------------------------------------------------- header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
fig.text(.045, .86, "Where", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .74, "languages", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .62, "come from", fontproperties=DISP, fontsize=50, color=HOT, va="top")
fig.text(.047, .45, f"Every one of the world's\n{R['counts']['spoken']:,} spoken languages,\ncoloured by family:\n{R['counts']['families']} families and\n{R['counts']['isolates']} isolates.", fontproperties=SERP, fontsize=17, color=FG, va="top", linespacing=1.45)
fig.text(.047, .045, "maps.tristanhotham.com/language-origins", family=MONO, fontsize=11.5, color=MUT)
ax = fig.add_axes([.33, .02, .68, .96]); ax.set_facecolor(BG)
world(ax, fc=LAND, ec=BG, lw=.35, extent=(-12.6e6, 16.0e6, -5.9e6, 8.4e6))
lang_points(ax, s=2.6, only=lambda l: l[4] >= -1)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
from PIL import Image
assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print("figures done:", sorted(os.listdir(PAP)), sorted(f for f in os.listdir(BLOGD) if f.endswith(".png")))
