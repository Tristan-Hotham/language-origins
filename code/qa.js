// QA: open index.html at 1280 px and 390 px, record console errors, take screenshots of key states into qa/.
// Usage: node code/qa.js   (serves the repo root on a local port; web tiles and fonts are blocked offline and ignored;
// Leaflet is served from a local npm copy of the same version: set LEAFLET_DIR to a folder holding leaflet/dist)
const { chromium } = require(process.env.PW || "playwright");
const http = require("http"), fs = require("fs"), path = require("path");
const PORT = +(process.env.QAPORT || 8793);
const ROOT = path.resolve(__dirname, ".."), OUT = path.join(ROOT, "qa");
const LDIR = process.env.LEAFLET_DIR || "/tmp/claude-0/node_modules/leaflet/dist";
const TYPES = { ".html": "text/html", ".json": "application/json", ".png": "image/png", ".js": "text/javascript" };
const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split("?")[0]); if (p.endsWith("/")) p += "index.html"; const f = path.join(ROOT, p);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream" }); s.end(d); }); });
const atlas = async pg => { await (await pg.$("#atlas")).scrollIntoViewIfNeeded(); };
const SCEN = [
  ["family", async pg => {}],
  ["ie_branches", async pg => { await pg.evaluate(() => pickNode(NIDX["indo1319"], true)); }],
  ["germanic", async pg => { await pg.evaluate(() => pickNode(NIDX["germ1287"], true)); }],
  ["english", async pg => { await pg.evaluate(() => pickLang(LG.findIndex(l => l[0] === "stan1293"), true)); }],
  ["isolates", async pg => { await pg.evaluate(() => pickIsolates()); }],
  ["aes", async pg => { await pg.click('#modeRow .btn[data-m="aes"]'); }],
  ["speakers", async pg => { await pg.click('#modeRow .btn[data-m="speakers"]'); }],
  ["div_langs", async pg => { await pg.click('#modeRow .btn[data-m="divn"]'); }],
  ["div_lineages_ng", async pg => { await pg.click('#modeRow .btn[data-m="divl"]'); await pg.evaluate(() => map.fitBounds([[-11, 130], [0, 156]])); }],
  ["origins", async pg => { await pg.click("#origBtn"); }],
  ["origins_ie", async pg => { await pg.click("#origBtn"); await pg.evaluate(() => pickNode(NIDX["indo1319"], true)); }],
  ["search", async pg => { await pg.fill("#q", "Basq"); await pg.waitForTimeout(400); await pg.screenshot({ path: `${OUT}/${pg._tag}_search_list.png` }); await pg.keyboard.press("Enter"); }],
  ["layers_panel", async pg => { await pg.click(".lyrBtn"); }],
];
(async () => {
  await new Promise(r => srv.listen(PORT, r));
  const b = await chromium.launch();
  const errs = [];
  for (const [w, h, tag] of [[1280, 900, "desk"], [390, 844, "phone"]]) {
    const open = async () => {
      const pg = await b.newPage({ viewport: { width: w, height: h } }); pg._tag = tag;
      pg.on("console", m => { if (m.type() === "error" && !/Failed to load resource|ERR_|net::/.test(m.text())) errs.push(`${tag}: ${m.text()}`); });
      pg.on("pageerror", e => errs.push(`${tag} pageerror: ${e.message}`));
      await pg.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
      await pg.route(/leaflet.min.js/, r => r.fulfill({ path: `${LDIR}/leaflet.js` }));
      await pg.route(/leaflet.min.css/, r => r.fulfill({ path: `${LDIR}/leaflet.css` }));
      await pg.addInitScript(() => { try { localStorage.clear(); } catch (e) {} });
      await pg.goto(`http://localhost:${PORT}/index.html`, { waitUntil: "networkidle" });
      await pg.waitForFunction(() => window.dataReady === true, null, { timeout: 15000 });
      await pg.waitForTimeout(600); return pg;
    };
    let pg = await open();
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (ov > 0) errs.push(`${tag}: horizontal overflow ${ov}px`);
    if (!(await pg.$(".mfs-btn"))) errs.push(`${tag}: no full-screen button`);
    await pg.screenshot({ path: `${OUT}/${tag}_top.png` });
    for (const id of ["famChart", "ctyChart", "aesChart", "spChart", "homeTable", "origChart"]) {
      const e = await pg.$("#" + id); await e.scrollIntoViewIfNeeded(); await pg.waitForTimeout(150); await e.screenshot({ path: `${OUT}/${tag}_chart_${id}.png` });
    }
    await pg.click("#theme"); await pg.waitForTimeout(500); await pg.evaluate(() => window.scrollTo(0, 0)); await pg.screenshot({ path: `${OUT}/${tag}_dark_top.png` });
    await atlas(pg); await pg.evaluate(() => pickNode(NIDX["aust1307"], true)); await pg.waitForTimeout(800);
    await (await pg.$("#atlas")).screenshot({ path: `${OUT}/${tag}_dark_map.png` });
    await pg.close();
    for (const [name, fn] of SCEN) {
      pg = await open();
      try { await atlas(pg); await fn(pg); await pg.waitForTimeout(1500); await (await pg.$("#atlas")).screenshot({ path: `${OUT}/${tag}_${name}.png` }); }
      catch (e) { errs.push(`${tag} ${name}: ${e.message.split("\n")[0]}`); }
      await pg.close();
    }
    // full screen
    pg = await open(); await atlas(pg); await pg.click(".mfs-btn"); await pg.waitForTimeout(600); await pg.screenshot({ path: `${OUT}/${tag}_fullscreen.png` }); await pg.close();
  }
  await b.close(); srv.close();
  console.log(errs.length ? errs.join("\n") : "no console errors");
})();
