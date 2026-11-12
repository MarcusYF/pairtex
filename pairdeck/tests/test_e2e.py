#!/usr/bin/env python3
"""End-to-end test of PairDeck: setup, new, qa (lint), bundle, seed, snapshot, the review server, watch, resolve, learn.

Everything runs in a temporary HOME and data home; nothing outside them is touched. Screenshots (qa, card) run only when
Chrome or Chromium is found; seeding renders PDF pages only when a renderer exists (macOS swift, pdftoppm or mutool).
Run: python3 tests/test_e2e.py
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

PD = Path(__file__).resolve().parent.parent / "bin" / "pairdeck"
TMP = Path(tempfile.mkdtemp(prefix="pairdeck-test-"))
HOME = TMP / "home"
DATA = TMP / "data"
ENV = dict(os.environ, HOME=str(HOME), PAIRDECK_HOME=str(DATA), GIT_TERMINAL_PROMPT="0",
           GIT_CONFIG_GLOBAL=str(TMP / "gitconfig"), GIT_CONFIG_NOSYSTEM="1")
DECK_DIR = TMP / "decks" / "demo"
passed = 0
procs: list = []


def pd(*args, expect=0, timeout=120):
    r = subprocess.run([sys.executable, str(PD), *args], env=ENV, capture_output=True, text=True, timeout=timeout)
    if expect is not None and r.returncode != expect:
        raise AssertionError(f"pairdeck {' '.join(args)}: exit {r.returncode}, expected {expect}\n--- stdout\n{r.stdout}\n"
                             f"--- stderr\n{r.stderr}")
    return r.stdout


def pd_bg(*args):
    p = subprocess.Popen([sys.executable, str(PD), *args], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    procs.append(p)
    return p


def ok(cond, what):
    global passed
    if not cond:
        raise AssertionError(what)
    passed += 1
    print(f"  ok  {what}")


def have_chrome() -> bool:
    return any(c and os.path.exists(c) for c in [os.environ.get("CHROME"),
                                                 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                                                 "/Applications/Chromium.app/Contents/MacOS/Chromium",
                                                 shutil.which("google-chrome"), shutil.which("chromium")])


def have_pdf_renderer() -> bool:
    return bool((sys.platform == "darwin" and shutil.which("swift")) or shutil.which("pdftoppm") or shutil.which("mutool"))


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def http(method, url, body=None, ctype="application/json", headers=None):
    data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": ctype, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def events() -> list:
    f = DATA / "vault" / "evidence.jsonl"
    return [json.loads(x) for x in f.read_text().splitlines() if x.strip()] if f.exists() else []


# ------------------------------------------------------------------------------------------------ fixtures

SLIDES = """
  <section class="dk-slide" data-label="Setting">
    <div class="dk-inner">
      <h2 class="dk-h">Two treatments, two kinds of patients</h2>
      <figure class="dk-fig"><svg viewBox="0 0 600 200"><svg x="250" y="50" width="56" height="56" class="icon c-people"><use href="_deck/icons.svg#person"/></svg>
      <g data-step="1"><rect class="f-people-soft s-people" x="20" y="40" width="200" height="80" rx="6"/>
      <text x="120" y="88" text-anchor="middle" class="t-people" font-size="20">treatment A</text></g></svg></figure>
      <p class="dk-take" data-step="1">Patients differ before any treatment starts.</p>
    </div>
  </section>

  <section class="dk-slide" data-label="Result">
    <div class="dk-inner">
      <h2 class="dk-h">A wins in each group</h2>
      <figure class="dk-fig"><svg viewBox="0 0 600 200"><rect class="f-teal dk-grow" x="20" y="40" width="300" height="30"/>
      <text x="330" y="62" class="t-teal" font-size="18">93%</text></svg></figure>
      <p class="dk-take" data-step="1">Within each group, A does better.</p>
    </div>
  </section>
"""


def fill_deck(text: str) -> str:
    start = text.index("  <!-- 2 Setting")
    end = text.index("  <!-- Last: takeaways -->")
    text = text[:start] + SLIDES + "\n" + text[end:]
    for old, new in [("TODO: the question this answers, in plain words", "Why the totals can mislead"),
                     ("TODO: authors · occasion and year", "A test deck"),
                     ("TODO: what this means", "What it means"), ("TODO: links for readers who want more (or delete this note)",
                                                                   "No links")]:
        text = text.replace(old, new)
    return text.replace("<span class=\"t\">TODO</span><span class=\"d\">TODO</span>",
                        "<span class=\"t\">Look inside groups</span><span class=\"d\">Totals mix two things.</span>")


def make_pptx(path: Path):
    A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    P = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    R = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

    def rels(*items):
        return ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                'relationships">' + "".join(f'<Relationship Id="{i}" Type="{REL}/{t}" Target="{g}"/>' for i, t, g in items)
                + "</Relationships>")

    def sp(text, ph=None, colour=None, font=None):
        php = f'<p:nvPr><p:ph type="{ph}"/></p:nvPr>' if ph else "<p:nvPr/>"
        fill = f'<a:solidFill><a:srgbClr val="{colour}"/></a:solidFill>' if colour else ""
        latin = f'<a:latin typeface="{font}"/>' if font else ""
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="s"/><p:cNvSpPr/>{php}</p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/>'
                f'<a:p><a:r><a:rPr lang="en-US" sz="2800">{fill}{latin}</a:rPr><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')

    def slide(title, body):
        return (f'<?xml version="1.0" encoding="UTF-8"?><p:sld {A} {P} {R}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
                f'<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{sp(title, "title", font="Georgia")}'
                f'{sp(body, None, "2E75B6", "Verdana")}<p:pic><p:nvPicPr><p:cNvPr id="4" name="pic"/><p:cNvPicPr/><p:nvPr/>'
                f'</p:nvPicPr><p:blipFill/><p:spPr/></p:pic></p:spTree></p:cSld></p:sld>')

    notes = (f'<?xml version="1.0" encoding="UTF-8"?><p:notes {A} {P} {R}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
             f'<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{sp("Say the punchline slowly.", "body")}</p:spTree></p:cSld></p:notes>')
    theme = (f'<?xml version="1.0" encoding="UTF-8"?><a:theme {A} name="T"><a:themeElements><a:clrScheme name="c">'
             '<a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>'
             '<a:dk2><a:srgbClr val="1F3864"/></a:dk2><a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>'
             '<a:accent1><a:srgbClr val="2E75B6"/></a:accent1><a:accent2><a:srgbClr val="C55A11"/></a:accent2></a:clrScheme>'
             '<a:fontScheme name="f"><a:majorFont><a:latin typeface="Georgia"/></a:majorFont><a:minorFont><a:latin typeface="Verdana"/>'
             '</a:minorFont></a:fontScheme></a:themeElements></a:theme>')
    layout = (f'<?xml version="1.0" encoding="UTF-8"?><p:sldLayout {A} {P} {R}><p:cSld name="Title and Content"><p:spTree>'
              '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld></p:sldLayout>')
    master = (f'<?xml version="1.0" encoding="UTF-8"?><p:sldMaster {A} {P} {R}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
              '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld></p:sldMaster>')
    pres = (f'<?xml version="1.0" encoding="UTF-8"?><p:presentation {A} {P} {R}><p:sldMasterIdLst><p:sldMasterId id="2147483648" '
            'r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst><p:sldId id="256" r:id="rId2"/><p:sldId id="257" r:id="rId3"/></p:sldIdLst>'
            '<p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/'
                   'content-types"/>')
        z.writestr("_rels/.rels", rels(("rId1", "officeDocument", "ppt/presentation.xml")))
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", rels(("rId1", "slideMaster", "slideMasters/slideMaster1.xml"),
                                                           ("rId2", "slide", "slides/slide1.xml"),
                                                           ("rId3", "slide", "slides/slide2.xml")))
        z.writestr("ppt/slideMasters/slideMaster1.xml", master)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", rels(("rId1", "theme", "../theme/theme1.xml")))
        z.writestr("ppt/theme/theme1.xml", theme)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
        for n, (t, b) in enumerate([("Why totals mislead", "Groups differ in size"), ("Look within groups", "Then compare")], 1):
            z.writestr(f"ppt/slides/slide{n}.xml", slide(t, b))
            z.writestr(f"ppt/slides/_rels/slide{n}.xml.rels", rels(("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
                                                                   ("rId2", "notesSlide", f"../notesSlides/notesSlide{n}.xml")))
            z.writestr(f"ppt/notesSlides/notesSlide{n}.xml", notes)


def make_pdf(path: Path):
    """Two pages: a heading in Helvetica and a blue block, written by hand with a correct cross-reference table."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>"]
    contents = []
    for n, title in enumerate(["Old talk, page one", "Old talk, page two"]):
        stream = (f"0.18 0.46 0.71 rg 40 40 520 120 re f 0 0 0 rg BT /F1 28 Tf 40 300 Td ({title}) Tj ET").encode()
        contents.append(stream)
    objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 640 360] /Contents 5 0 R /Resources << /Font << /F1 7 0 R >> >> >>")
    objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 640 360] /Contents 6 0 R /Resources << /Font << /F1 7 0 R >> >> >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    bodies = [o.encode() for o in objs] + [b"<< /Length %d >>\nstream\n" % len(c) + c + b"\nendstream" for c in contents] + \
        [b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, b in enumerate(bodies, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + b + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(bodies) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(bodies) + 1, xref)
    path.write_bytes(bytes(out))


HTML_DECK = """<!doctype html><html><head><title>An old deck</title><style>
:root { --accent: #3A7D44; --ink: #222222; --font: "Source Serif 4", Georgia, serif; }
body { font-family: var(--font); color: var(--ink); }
h2 { color: var(--accent); font-family: "Source Sans 3", sans-serif; }
.box { fill: var(--accent); }
</style></head><body>
<section class="slide" data-label="Opening"><h2>A question first</h2><p>One sentence that sets the scene.</p>
<aside class="notes">Pause here and ask the room.</aside></section>
<section class="slide"><h2>Then the picture</h2><svg><rect class="box" width="10" height="10"/></svg><p>Short caption.</p></section>
</body></html>"""


# ------------------------------------------------------------------------------------------------ the test

def main():
    HOME.mkdir(parents=True)
    print(f"temp folder: {TMP}")
    try:
        run()
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
    print(f"\nall {passed} checks passed")
    shutil.rmtree(TMP, ignore_errors=True)


def run():
    # setup, paths, status
    out = pd("setup", "--name", "Ada Lovelace", "--agent", "Claude")
    ok((DATA / "vault" / "STYLE.md").exists() and (DATA / "vault" / "preferences.md").exists(), "setup makes the vault")
    style = (DATA / "vault" / "STYLE.md").read_text()
    ok("## Palette, type and layout" in style and "## What Ada undid" in style, "STYLE.md has the contract's skeleton")
    ok((DATA / ".git").exists() and "PairDeck data home" in subprocess.run(
        ["git", "-C", str(DATA), "log", "--oneline"], capture_output=True, text=True, env=ENV).stdout,
       "the data home is a git repository with a first commit")
    ok(json.loads(pd("paths", "--json"))["data home"] == str(DATA), "paths names the data home")

    # new: scaffold and register
    pd("new", "demo", "--title", "Demo|Deck", "--dir", str(DECK_DIR))
    deck = DECK_DIR / "index.html"
    ok(deck.exists() and (DECK_DIR / "_deck" / "deck.js").exists(), "new scaffolds the deck and copies the engine")
    cfg = json.loads((DATA / "projects" / "demo" / "project.json").read_text())
    ok(cfg["dir"] == str(DECK_DIR) and (DATA / "projects" / "demo" / "NOTES.md").exists(), "new registers the deck")
    out = pd("qa", "demo", "--no-shots", expect=1)
    ok("unfinished placeholders" in out, "qa's lint catches the scaffold's TODOs")
    deck.write_text(fill_deck(deck.read_text()))
    out = pd("qa", "demo", "--no-shots")
    ok("ERROR" not in out and "Slides: 4" in out, "qa's lint passes on a filled deck")
    if have_chrome():
        out = pd("qa", "demo", "--slides", "2", "--modes", "light", timeout=300)
        ok((DATA / "projects" / "demo" / "qa" / "light-02.png").exists(), "qa screenshots a slide (Chrome)")
        card = TMP / "card.png"
        pd("card", "demo", "-o", str(card), timeout=180)
        ok(card.exists() and card.stat().st_size > 5000, "card renders a share image (Chrome)")
    else:
        print("  --  no Chrome or Chromium: skipped the screenshot checks")
    single = TMP / "single.html"
    out = pd("bundle", "demo", "-o", str(single))
    page = single.read_text()
    ok('<symbol id="dkicon-person"' in page and 'href="#dkicon-person"' in page and "icons.svg" not in page,
       "bundle inlines the icons the deck uses")
    ok("window.Deck" in page and "@font-face" in page and "deck.css" not in page, "bundle inlines the engine and fonts")

    # seed from past decks
    src = TMP / "old-decks"
    (src / "nested").mkdir(parents=True)
    make_pptx(src / "talk.pptx")
    make_pdf(src / "nested" / "export.pdf")
    (src / "nested" / "slides.html").write_text(HTML_DECK)
    (src / "ignored.txt").write_text("not a deck")
    (src / "keynote.key").write_bytes(b"PK")
    before = {p: p.stat().st_mtime_ns for p in src.rglob("*") if p.is_file()}
    out = pd("seed", str(src), "--note", "three old decks", timeout=300)
    sd = DATA / "vault" / "seed" / "seed-001"
    man = json.loads((sd / "manifest.json").read_text())
    stats = json.loads((sd / "stats.json").read_text())
    samples = (sd / "samples.md").read_text()
    fmts = sorted(f["format"] for f in man["files"] if not f.get("skipped"))
    ok(fmts == ["html", "pdf", "pptx"], "seed reads a .pptx, a .pdf and an .html deck from a folder, recursively")
    ok(any("export to PDF or PPTX" in (f.get("skipped") or "") for f in man["files"]), "seed skips .key with advice")
    pal = {p["hex"] for p in stats["palette"]}
    ok("#2E75B6" in pal and "#3A7D44" in pal, "the palette has the PPTX theme colour and the HTML deck's CSS colour")
    fonts = {f["name"] for f in stats["fonts"]}
    ok({"Georgia", "Verdana", "Source Serif 4"} <= fonts, "fonts come from the PPTX theme and runs, and the HTML's CSS")
    ok("Why totals mislead" in samples and "Say the punchline slowly." in samples and "Pause here and ask the room." in samples,
       "samples.md has slide titles and speaker notes (PPTX and HTML)")
    ok(stats["slides"] == 6 and stats["words_per_slide"].get("median", 0) > 0, "stats count slides and words per slide")
    ok(all(f.get("sha256") and len(f["sha256"]) == 64 for f in man["files"] if not f.get("skipped")), "the manifest has hashes")
    if have_pdf_renderer():
        ok(len(list((sd / "pages").glob("export-*.png"))) == 2, "PDF pages are rendered to PNG")
        pdf_entry = [f for f in man["files"] if f.get("format") == "pdf"][0]
        ok("Helvetica" in fonts and pdf_entry["pages"] == 2, "PDF fonts and page count are read")
        ok(any(p["role_hint"] == "accent" and p["hex"].startswith("#2") for p in stats["palette"]),
           "the PDF's blue block shows in the palette (from pixels)")
    else:
        print("  --  no PDF renderer: skipped the page-image checks")
    ok(before == {p: p.stat().st_mtime_ns for p in src.rglob("*") if p.is_file()}, "seed never touches its inputs")
    seeds = [e for e in events() if e["kind"] == "seed"]
    ok(len(seeds) == 3 and all(e["project"] is None and e["seed"] == "seed-001" for e in seeds), "one seed event per file")
    out = pd("seed", "--list")
    ok("seed-001" in out and "three old decks" in out and "waiting: E" in out, "seed --list shows the seed, its note and its events")
    pd("seed", str(src / "talk.pptx"))
    out = pd("seed", "--forget", "seed-002")
    gone = [e for e in events() if e.get("seed") == "seed-002"]
    ok(not (DATA / "vault" / "seed" / "seed-002").exists() and gone
       and all(e.get("discarded", {}).get("why") == "seed forgotten" for e in gone),
       "seed --forget removes the folder and discards its events")
    pd("learn", "--ack", *[e["id"] for e in seeds])

    # snapshot, review, a comment, watch
    out = pd("snapshot", "demo", "-m", "first build")
    ok("snapshot 0001" in out, "snapshot records the agent's version")
    port = free_port()
    srv = pd_bg("review", "demo", "--port", str(port))
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if http("GET", base + "/__pairdeck/state")[0] == 200:
                break
        except OSError:
            pass
        time.sleep(0.1)
    code, page = http("GET", base + "/index.html")
    ok(code == 200 and "/__pairdeck/overlay.js" in page and "window.PAIRDECK" in page, "review injects the comment overlay")
    ok("__pairdeck" not in deck.read_text(), "the overlay is never written into the deck")
    ok(http("GET", base + "/__pairdeck/overlay.js")[0] == 200, "review serves the overlay script")
    code, _ = http("POST", base + "/__pairdeck/comments", {"text": "x", "slide": 1}, ctype="text/plain")
    ok(code == 415, "review refuses a comment that is not JSON (no cross-site form posts)")
    code, _ = http("POST", base + "/__pairdeck/comments", {"text": "x", "slide": 1}, headers={"Origin": "http://evil.example"})
    ok(code == 403, "review refuses a cross-origin comment")
    code, _ = http("GET", base + "/../../etc/passwd")
    ok(code in (403, 404), "review serves nothing outside the deck's folder")
    code, body = http("POST", base + "/__pairdeck/comments",
                      {"text": "Make the 93% bar thicker; the label is hard to read.", "slide": 3, "step": 1, "steps": 1,
                       "label": "Result", "title": "A wins in each group", "box": {"x": 0.1, "y": 0.3, "w": 0.4, "h": 0.2},
                       "anchor": {"i": 1, "x": 0.05, "y": 0.2, "w": 0.6, "h": 0.3}, "under": "93%"})
    rec = json.loads(body)
    ok(code == 200 and rec["id"] == "c1" and rec["author"] == "Ada", "a comment posted on the review page gets an id")
    first = json.loads((DATA / "projects" / "demo" / "comments.jsonl").read_text().splitlines()[0])
    ok(first["box"]["w"] == 0.4 and first["anchor"] == {"i": 1, "x": 0.05, "y": 0.2, "w": 0.6, "h": 0.3},
       "comments go to comments.jsonl in the data home, with the box and its anchor")
    code, _ = http("POST", base + "/__pairdeck/comments", {"text": "x", "slide": 1, "anchor": {"i": "two"}})
    ok(code == 400, "a malformed box anchor is refused")
    out = pd("watch", "demo", "--settle", "0.3", "--interval", "0.1", timeout=60)
    ok("## c1 · slide 3 (Result)" in out and "Make the 93% bar thicker" in out and "x 0.10–0.50" in out
       and "under it: \"93%\"" in out, "watch prints the comment with its slide, box and the words under it")
    ok("sha " in out and "STYLE.md" in out and "review page: http://127.0.0.1" in out, "the batch names STYLE.md's sha and the page")
    out = pd("watch", "demo", "--once", expect=1)
    ok("nothing ready" in out, "a comment is sent once")

    # resolve: the reply shows on the review page
    deck.write_text(deck.read_text().replace('height="30"/>', 'height="44"/>'))
    pd("resolve", "demo", "c1", "Made the bar 44 units tall and kept the label beside it.")
    state = json.loads(http("GET", base + "/__pairdeck/state")[1])
    c1 = state["comments"][0]
    ok(c1["status"] == "answered" and "44 units" in c1["replies"][0]["text"], "resolve's reply shows on the review page")
    out = pd("watch", "demo", "--once", expect=4)
    ok("run `pairdeck snapshot demo` first" in out, "watch refuses to start while the agent's answered edits are unsnapshotted")
    lock = DATA / "projects" / "demo" / "watch.lock"
    lock.write_text(json.dumps({"pid": os.getpid(), "started": "now"}))
    ok("watcher is running" in pd("snapshot", "demo", expect=5), "snapshot waits while a watcher runs")
    lock.unlink()
    pd("snapshot", "demo", "-m", "c1")

    # Keep, and the author's own edit after the snapshot
    code, _ = http("POST", base + "/__pairdeck/keep", {"id": "c1"})
    ok(code == 200, "the author presses Keep on the answer")
    text = deck.read_text()
    deck.write_text(text.replace("Patients differ before any treatment starts.", "The groups differ before treatment."))
    out = pd("watch", "demo", "--settle", "0.3", "--interval", "0.1", timeout=60)
    ok("revised" in out and "slide 2 (Setting)" in out and "-      <p class=\"dk-take\" data-step=\"1\">Patients differ" in out
       and "+      <p class=\"dk-take\" data-step=\"1\">The groups differ" in out,
       "an author's edit after the snapshot is a `revised` event with a diff in the batch")
    rev = [e for e in events() if e["kind"] == "revised"]
    ok(len(rev) == 1 and "Patients differ" in rev[0]["before"] and "The groups differ" in rev[0]["after"],
       "the revised event keeps the agent's version and the author's")
    ok(any(e["kind"] == "kept" and e["cid"] == "c1" for e in events()), "Keep becomes `kept` evidence")

    # a stated preference, and a revert
    http("POST", base + "/__pairdeck/comments", {"text": "Never use a pie chart in my decks; always bars.", "slide": 2})
    out = pd("watch", "demo", "--settle", "0.3", "--interval", "0.1", timeout=60)
    ok("## c2" in out and any(e["kind"] == "stated" and e["cid"] == "c2" for e in events()),
       "a comment stating a general preference becomes `stated` evidence")
    agent_v = deck.read_text()
    deck.write_text(agent_v.replace("A wins in each group", "Treatment A wins in each group"))
    pd("resolve", "demo", "c2", "Noted: bars, never pies.")
    pd("snapshot", "demo", "-m", "c2 and a new headline")
    deck.write_text(agent_v)  # the author restores the headline the agent changed
    pd("watch", "demo", "--settle", "0.3", "--interval", "0.1", timeout=60)
    ok(any(e["kind"] == "reverted" and e.get("slide") == 3 for e in events()), "restoring the earlier version is `reverted`")
    deck.write_text(agent_v.replace("<!-- Last: takeaways -->", "<section class=\"dk-slide\" data-label=\"Aside\"><div class=\"dk-inner\">"
                                    "<h2 class=\"dk-h\">An aside the author wrote</h2></div></section>\n  <!-- Last: takeaways -->"))
    pd("watch", "demo", "--settle", "0.3", "--interval", "0.1", timeout=60)
    ok(any(e["kind"] == "own_edit" and e.get("change") == "added" for e in events()), "a slide the author adds is `own_edit`")

    # one watcher per deck
    w = pd_bg("watch", "demo", "--settle", "60")
    for _ in range(50):
        if lock.exists():
            break
        time.sleep(0.1)
    ok("another watcher is running" in pd("watch", "demo", "--once", expect=5), "a second watcher is refused (one per deck)")
    w.terminate()
    w.wait(timeout=10)
    ok(not lock.exists(), "a stopped watcher releases its lock")

    # learn: list, ack, discard
    out = pd("learn", "demo")
    ok("revised" in out and "stated" in out and "kept" in out and "pairdeck learn --ack" in out, "learn shows the evidence in full")
    pend = [e["id"] for e in events() if e.get("project") == "demo" and not e.get("acked") and not e.get("discarded")]
    pd("learn", "demo", "--discard", pend[0], "--why", "a test edit")
    ok("--why" in pd("learn", "demo", "--discard", pend[1], expect=1), "discard needs a reason")
    pd("learn", "demo", "--ack", *pend[1:])
    ok("no style evidence waiting" in pd("learn", "demo"), "acked and discarded events leave the queue")
    ok([e for e in events() if e["id"] == pend[0]][0]["discarded"]["why"] == "a test edit", "a discarded event keeps the reason")
    out = pd("status", "demo")
    ok("review page: http://127.0.0.1" in out and "comments: 1 answered, 1 kept" in out, "status shows the page and the comments")
    srv.terminate()
    srv.wait(timeout=10)
    ok(not (DATA / "projects" / "demo" / "server.json").exists(), "the review server cleans up when stopped")
    out = pd("status")
    ok("demo:" in out and "seeds: 1" in out, "status without a slug lists the decks and seeds")


if __name__ == "__main__":
    main()
