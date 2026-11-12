#!/usr/bin/env python3
"""End-to-end test of PairTalk with a temporary HOME: setup, a new talk, the review server and its inbox, watch batches,
resolve, snapshots and style evidence (revised, reverted, stated; coauthors never counted), script apply, seeding from a
generated .pptx with speaker notes, learn --ack/--discard, the watch lock, the shared site against a stand-in for Wrangler
and D1 (sqlite), and, when Chrome is installed, screenshots and the bundle.

Run: python3 tests/test_e2e.py   (needs git and Node 22+ with `npm install` done in the PairTalk folder)
"""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
PT = APP / "bin" / "pairtalk"
TMP = Path(tempfile.mkdtemp(prefix="pairtalk-test-"))
HOME = TMP / "home"
DATA = TMP / "data"
TALK = TMP / "talks" / "demo"
ENV = dict(os.environ, HOME=str(HOME), PAIRTALK_HOME=str(DATA), GIT_TERMINAL_PROMPT="0")
ENV.pop("PAIRDECK_HOME", None)
passed = 0
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def pt(*args, expect=0, timeout=180, env=None):
    r = subprocess.run([sys.executable, str(PT), *args], env=env or ENV, capture_output=True, text=True, timeout=timeout)
    if expect is not None and r.returncode != expect:
        raise AssertionError(f"pairtalk {' '.join(args)}: exit {r.returncode}, expected {expect}\n--- stdout\n{r.stdout}\n--- stderr\n{r.stderr}")
    return r.stdout + r.stderr


def ok(cond, what):
    global passed
    if not cond:
        raise AssertionError(what)
    passed += 1
    print(f"  ok  {what}")


def events():
    f = DATA / "vault" / "evidence.jsonl"
    return [json.loads(x) for x in f.read_text().splitlines() if x.strip()] if f.exists() else []


def baseline():
    return json.loads((DATA / "projects" / "demo" / "baseline.json").read_text())


def set_note(path: Path, old: str, new: str):
    """The agent (or the owner) edits a note string in a slide file."""
    s = path.read_text()
    assert old in s, f"{old!r} not in {path.name}"
    path.write_text(s.replace(old, new, 1))


def set_script(key: str, text: str):
    """The owner edits one block of SCRIPT.md in their editor."""
    script = TALK / "SCRIPT.md"
    s = script.read_text()
    pat = re.compile(r'(<!-- slide-note \{"sid":"%s","k":%s,[^\n]*-->\n)([\s\S]*?)(\n<!-- /slide-note -->)' % tuple(key.split(".")))
    assert pat.search(s), key
    script.write_text(pat.sub(lambda m: m.group(1) + text + m.group(3), s, count=1))


def script_text(key: str) -> str:
    s = (TALK / "SCRIPT.md").read_text()
    m = re.search(r'<!-- slide-note \{"sid":"%s","k":%s,[^\n]*-->\n([\s\S]*?)\n<!-- /slide-note -->' % tuple(key.split(".")), s)
    return m.group(1)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def http(url, data=None, origin=None, method=None):
    headers = {"Content-Type": "application/json"} if data is not None else {}
    if origin:
        headers["Origin"] = origin
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read()
            return r.status, (json.loads(body) if r.headers.get("Content-Type", "").startswith("application/json") else body)
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, body


def make_pptx(path: Path, notes: list):
    """A minimal .pptx: slides with speaker notes (and a slide-number placeholder that must not count as notes)."""
    P = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" ' \
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ' \
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        ids = "".join(f'<p:sldId id="{256 + i}" r:id="rId{i + 1}"/>' for i in range(len(notes)))
        z.writestr("ppt/presentation.xml", f'<?xml version="1.0"?><p:presentation {P}><p:sldIdLst>{ids}</p:sldIdLst></p:presentation>')
        rels = "".join(f'<Relationship Id="rId{i + 1}" Type="{REL}/slide" Target="slides/slide{i + 1}.xml"/>' for i in range(len(notes)))
        z.writestr("ppt/_rels/presentation.xml.rels", f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        for i, text in enumerate(notes):
            n = i + 1
            z.writestr(f"ppt/slides/slide{n}.xml", f'<?xml version="1.0"?><p:sld {P}><p:cSld><p:spTree/></p:cSld></p:sld>')
            z.writestr(f"ppt/slides/_rels/slide{n}.xml.rels", f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       f'<Relationship Id="rId1" Type="{REL}/notesSlide" Target="../notesSlides/notesSlide{n}.xml"/></Relationships>')
            paras = "".join(f"<a:p><a:r><a:t>{x}</a:t></a:r></a:p>" for x in text.split("\n"))
            z.writestr(f"ppt/notesSlides/notesSlide{n}.xml", f'<?xml version="1.0"?><p:notes {P}><p:cSld><p:spTree>'
                       f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/><p:cNvSpPr/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:txBody>{paras}</p:txBody></p:sp>'
                       f'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Num"/><p:cNvSpPr/><p:nvPr><p:ph type="sldNum" idx="5"/></p:nvPr></p:nvSpPr><p:txBody><a:p><a:r><a:t>{n}</a:t></a:r></a:p></p:txBody></p:sp>'
                       f'</p:spTree></p:cSld></p:notes>')


SEED_STANDIN = r'''#!/usr/bin/env python3
"""A stand-in for shared/seed_visual.py with its interface: PATH... --out DIR --kind talk --json writes manifest.json,
stats.json, samples.md and pages/*.png, and prints the manifest."""
import base64, json, sys
from pathlib import Path
args = sys.argv[1:]
out = Path(args[args.index("--out") + 1]); kind = args[args.index("--kind") + 1]
files = [a for i, a in enumerate(args) if not a.startswith("--") and args[i - 1] not in ("--out", "--kind")]
(out / "pages").mkdir(parents=True, exist_ok=True)
png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
for i, f in enumerate(files):
    (out / "pages" / f"{i + 1:03d}-001.png").write_bytes(png)
manifest = {"kind": kind, "files": [{"path": f, "pages": 1} for f in files]}
(out / "manifest.json").write_text(json.dumps(manifest))
(out / "stats.json").write_text(json.dumps({"slides": len(files), "palette": [["#27709C", 0.3]]}))
(out / "samples.md").write_text("# Slides\n\nTitles and text of each slide.\n")
print(json.dumps(manifest))
'''

FAKE_WRANGLER = r'''#!/usr/bin/env python3
"""A stand-in for Wrangler: `d1 execute DB (--remote|--local) ... --json --command SQL` runs the SQL in a sqlite file
($FAKE_D1) and prints D1's JSON; every call is logged to $FAKE_WRANGLER_LOG."""
import json, os, sqlite3, sys
args = sys.argv[1:]
with open(os.environ["FAKE_WRANGLER_LOG"], "a") as f:
    f.write(json.dumps(args) + "\n")
if args[:2] != ["d1", "execute"] or "--command" not in args:
    sys.exit(0)
sql = args[args.index("--command") + 1]
db = sqlite3.connect(os.environ["FAKE_D1"]); db.row_factory = sqlite3.Row
out, buf = [], ""
for ch in sql:
    buf += ch
    if ch == ";" and sqlite3.complete_statement(buf):
        cur = db.execute(buf)
        out.append({"results": [dict(r) for r in cur.fetchall()], "success": True}); buf = ""
db.commit()
print(json.dumps(out))
'''


def main():
    print(f"scratch: {TMP}")
    HOME.mkdir(parents=True)

    print("setup")
    out = pt("setup", "--name", "Ada Lovelace", "--agent", "Claude")
    prof = json.loads((DATA / "profile.json").read_text())
    ok(prof["name"] == "Ada Lovelace" and prof["handle"] == "Ada", "setup writes the profile")
    ok((DATA / "vault" / "STYLE.md").exists() and "Pacing and script" in (DATA / "vault" / "STYLE.md").read_text(),
       "the vault starts from the template, with the Pacing and script table")
    ok((DATA / "vault" / "preferences.md").exists() and (DATA / "vault" / "evidence.jsonl").exists(), "preferences and evidence exist")
    ok((DATA / ".git").exists(), "the data home is a git repository")
    paths = json.loads(pt("paths", "--json"))
    ok(paths["talk style"] == str(DATA / "vault" / "STYLE.md") and str(HOME / ".pairdeck") in paths["visual look"],
       "paths names the vault and PairDeck's style guide")

    print("new")
    out = pt("new", "demo", "--example", "pagerank", "--dir", str(TALK))
    ok("12 slides" in out and "8 minutes" in out, "new copies the demo talk")
    index = (TALK / "index.html").read_text()
    ok("window.DECK_COMMENTS = 'demo'" in index and "window.DECK_MINUTES = 8" in index and "<title>How PageRank" in index,
       "index.html names the talk, its slot and its title")
    ok(len(re.findall(r"<!-- slide-note ", (TALK / "SCRIPT.md").read_text())) == 30, "SCRIPT.md has every note (30)")
    ok(all(v["by"] == "template" for v in baseline()["notes"].values()), "the first snapshot marks the example as template text")
    pt("new", "demo", "--title", "Again", "--dir", str(TMP / "talks" / "x"), expect=1)
    (TMP / "talks" / "full").mkdir(parents=True)
    (TMP / "talks" / "full" / "a.txt").write_text("x")
    pt("new", "other", "--title", "Other", "--dir", str(TMP / "talks" / "full"), expect=1)
    ok(True, "new refuses an existing name and a non-empty folder")

    print("the agent's work, then the owner's script edit: revised")
    votes = TALK / "slides" / "03_votes.js"
    old_v1 = script_text("VOTES.1")
    agent_v1 = "Here are the links between them. Each link is a vote: when D links to A, D's author says that A is worth reading."
    set_note(votes, old_v1, agent_v1)
    out = pt("snapshot", "demo")
    ok("1 note and 0 slide files changed by the agent" in out, "snapshot records the agent's note")
    ok(baseline()["notes"]["VOTES.1"] == {"text": agent_v1, "by": "agent", "prev": old_v1}, "the baseline knows the agent wrote VOTES.1")
    ok(script_text("VOTES.1") == agent_v1, "snapshot brings SCRIPT.md up to date")
    owner_v1 = "Now the links. A link is a vote: D links to A, so D vouches for A."
    set_script("VOTES.1", owner_v1)
    out = pt("watch", "demo", "--once")
    ok("## Script edits" in out and "VOTES.1" in out and "by Ada Lovelace (owner) · in SCRIPT.md" in out, "the batch shows the owner's script edit")
    ev = [e for e in events() if e.get("sid") == "VOTES"]
    ok(len(ev) == 1 and ev[0]["kind"] == "revised" and ev[0]["before"] == agent_v1 and ev[0]["after"] == owner_v1,
       "the owner's rewrite of the agent's note is revised evidence")
    ok("Talk style:" in out and "sha " in out and "Visual look: no PairDeck style guide" in out, "the batch names the STYLE.md sha and the look")
    pt("watch", "demo", "--once", expect=1)
    ok(True, "the same edit is not reported twice")

    print("unrecorded agent work is refused")
    set_note(votes, "Here is a tiny web: five pages, A to E.", "Here is a small web: five pages, A to E.")
    out = pt("watch", "demo", "--once", expect=4)
    ok("pairtalk snapshot" in out, "watch exits 4 when the agent changed slides without a snapshot")
    pt("script", "apply", "demo")
    ok(owner_v1 in votes.read_text(), "script apply writes the owner's SCRIPT.md edit into the slide")
    pt("snapshot", "demo")
    b = baseline()
    ok(b["notes"]["VOTES.1"]["by"] == "owner" and b["notes"]["VOTES.0"]["by"] == "agent" and not b["batch_open"],
       "after the snapshot the owner's text stays the owner's; the agent's edit is the agent's")

    print("an undo: reverted")
    surfer = TALK / "slides" / "04_surfer.js"
    old_s0 = script_text("SURFER.0")
    set_note(surfer, old_s0, "Picture a surfer who never stops clicking.")
    pt("snapshot", "demo")
    set_script("SURFER.0", old_s0)
    pt("watch", "demo", "--once")
    ev = [e for e in events() if e.get("sid") == "SURFER"]
    ok(len(ev) == 1 and ev[0]["kind"] == "reverted", "restoring the text the agent replaced is reverted evidence")
    pt("script", "apply", "demo")
    pt("snapshot", "demo")

    print("the review server")
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen([sys.executable, str(PT), "serve", "demo", "--port", str(port)], env=ENV,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for _ in range(100):
            try:
                status, page = http(base + "/")
                break
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.1)
        ok(status == 200 and b"window.DECK_COLLABORATION=true" in page and b'"Ada Lovelace"' in page,
           "serve injects collaboration and the owner's name into the page")
        ok(http(base + "/css/deck.css")[0] == 200 and http(base + "/../../etc/passwd")[0] == 404 and http(base + "/.gitignore")[0] == 404,
           "serve serves the talk folder and nothing outside it")
        ok(http(base + "/__comments?deck=demo")[1] == {"comments": []}, "the inbox starts empty")
        watcher = subprocess.Popen([sys.executable, str(PT), "watch", "demo", "--settle", "3", "--quiet", "0", "--interval", "0.3"],
                                   env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)   # in the background, as an agent runs it
        owner_c = {"deck": "demo", "n": 5, "k": 1, "sid": "SHARE", "title": "PageRank is the surfer's share of time",
                   "author": "Ada Lovelace", "text": "Never put two formulas on one line; split this one.",
                   "box": {"x": 700, "y": 740, "w": 520, "h": 110},
                   "images": [{"mime": "image/png", "w": 1, "h": 1, "data": base64.b64encode(PNG).decode()}]}
        ok(http(base + "/__comments", owner_c)[0] == 403, "a comment without the page's origin is refused")
        ok(http(base + "/__comments", {**owner_c, "deck": "other"}, origin=base)[0] == 400, "a comment for another talk is refused")
        ok(http(base + "/__comments", {**owner_c, "images": [{"mime": "image/png", "data": base64.b64encode(b"not a png").decode()}]},
                origin=base)[0] == 400, "an attachment that is not an image is refused")
        s, r1 = http(base + "/__comments", owner_c, origin=base)
        ok(s == 200 and r1["ok"] and re.fullmatch(r"[0-9a-z]{9}-[0-9a-f]{8}", r1["cid"]), "the owner's comment with a box and a screenshot is saved")
        co_c = {"deck": "demo", "n": 3, "k": 2, "sid": "VOTES", "title": "", "author": "Grace Hopper",
                "text": "Always use a bigger font for the badges.", "box": None}
        s, r2 = http(base + "/__comments", co_c, origin=base)
        ok(s == 200, "a coauthor's comment is saved")
        title0 = script_text("TITLE.0")
        s, e1 = http(base + "/__script", {"deck": "demo", "sid": "TITLE", "k": 0, "text": "Thanks for coming. One question today.",
                                          "orig": title0, "updated": None, "author": "Grace Hopper"}, origin=base)
        ok(s == 200 and e1["eid"] == "demo|TITLE|0", "a coauthor's script edit is saved")
        s, conflict = http(base + "/__script", {"deck": "demo", "sid": "TITLE", "k": 0, "text": "x", "orig": title0, "updated": None,
                                                "author": "Ada Lovelace"}, origin=base)
        ok(s == 409 and conflict["current"]["text"].startswith("Thanks for coming"), "a stale script save gets 409 and the current version")
        hook1 = script_text("HOOK.1")
        s, _ = http(base + "/__script", {"deck": "demo", "sid": "HOOK", "k": 1, "text": "Thousands of pages contain the word. Finding them is easy.",
                                         "orig": hook1, "updated": None, "author": "Ada Lovelace"}, origin=base)
        ok(s == 200, "the owner's script edit in the browser is saved")
        listed = http(base + "/__comments?deck=demo")[1]["comments"]
        ok(len(listed) == 2 and listed[0]["images"][0]["mime"] == "image/png" and "file" not in listed[0]["images"][0],
           "the panel lists both comments, without file paths")
        ok(http(base + f"/__comments/img?cid={r1['cid']}&i=0")[1] == PNG, "the attachment is served back")

        print("watch: one batch")
        before = len(events())
        out, err = watcher.communicate(timeout=120)
        ok(watcher.returncode == 0 and "# PairTalk · demo · 2 comments, 2 script edits" in out,
           "the background watcher waits for the feedback to settle, prints one batch and exits 0")
        ok(r1["cid"] in out and r2["cid"] in out, "the batch lists both comment ids")
        ok("slide 5 (SHARE) · click 1 · by Ada Lovelace (owner)" in out and "Box: x=700.0 y=740.0 w=520.0 h=110.0" in out,
           "the owner's comment comes with its slide, click and box")
        att = re.search(r"Attachment: (\S+)", out)
        ok(att and Path(att.group(1)).read_bytes() == PNG, "the batch names the saved screenshot")
        ok("by Grace Hopper (coauthor: fix it and answer it; it does not teach the style guide)" in out, "the coauthor's comment is marked")
        ok("TITLE.0 · by Grace Hopper (coauthor) · in the browser" in out and "HOOK.1 · by Ada Lovelace (owner) · in the browser" in out,
           "the batch lists the browser's script edits with their authors")
        new = events()[before:]
        ok(any(e["kind"] == "stated" and "Never put two formulas" in e["text"] for e in new), "the owner's 'never' is stated evidence")
        ok(not any("bigger font" in json.dumps(e) or "Thanks for coming" in json.dumps(e) for e in new),
           "the coauthor's comment and script edit teach nothing")
        ok(any(e["kind"] == "own_edit" and e.get("sid") == "HOOK" and e["via"] == "browser" for e in new),
           "the owner's browser edit of the template's text is own_edit evidence")
        pt("watch", "demo", "--once", expect=1)

        print("resolve")
        pt("resolve", "demo", r1["cid"], "Split it: r = Mr on its own line; the definition of M below.")
        c = [x for x in http(base + "/__comments?deck=demo")[1]["comments"] if x["cid"] == r1["cid"]][0]
        ok(c["status"] == "done" and c["reply"].startswith("Split it"), "the reply shows under the comment in the panel")
        out = pt("resolve", "demo", r2["cid"], "Badges are now 32 px.", "--stated", "bigger badges", expect=7)
        ok("coauthor" in out and not any("bigger badges" in json.dumps(e) for e in events()), "--stated refuses a coauthor's comment")
        ok([x for x in http(base + "/__comments?deck=demo")[1]["comments"] if x["cid"] == r2["cid"]][0]["status"] == "done",
           "the coauthor still gets the reply")
        pt("resolve", "demo", r1["cid"], "Split it.", "--stated", "one formula per line")
        ok(any(e["kind"] == "stated" and e["text"] == "one formula per line" for e in events()), "--stated records the owner's rule")
        pt("resolve", "demo", "0000000zz-00000000", "x", expect=1)

        print("script apply")
        out = pt("script", "apply", "demo")
        ok("applied 2 browser edit(s)" in out, "script apply writes the browser's edits into the slides")
        ok("One question today." in (TALK / "slides" / "01_title.js").read_text() and script_text("TITLE.0").startswith("Thanks for coming"),
           "the slide and SCRIPT.md carry the coauthor's wording")
        rows = http(base + "/__script?deck=demo")[1]
        ok(not rows["open"] and len(rows["rows"]) == 2, "the applied edits are closed")
        pt("snapshot", "demo")
        b = baseline()
        ok(b["notes"]["TITLE.0"]["by"] == "coauthor" and b["notes"]["HOOK.1"]["by"] == "owner", "the snapshot keeps who wrote each note")
    finally:
        server.terminate()
        server.wait(timeout=10)

    print("learn")
    out = pt("learn", "demo")
    pend = re.findall(r"^### (E\d+)", out, re.M)
    ok(len(pend) >= 4 and "revised" in out and "reverted" in out, "learn shows the talk's pending evidence")
    pt("learn", "--discard", pend[0], expect=1)
    pt("learn", "--discard", pend[0], "--why", "test: not the owner's writing")
    pt("learn", "--ack", *pend[1:])
    ok(pt("learn", "demo").strip() == "no talk-style evidence waiting", "--ack and --discard clear the queue")
    ok([e for e in events() if e["id"] == pend[0]][0]["discarded"]["why"].startswith("test"), "a discarded event keeps the reason")

    print("the watch lock")
    w = subprocess.Popen([sys.executable, str(PT), "watch", "demo", "--interval", "0.5"], env=ENV, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    lock = DATA / "projects" / "demo" / "watch.lock"
    for _ in range(100):
        if lock.exists():
            break
        time.sleep(0.1)
    out = pt("watch", "demo", "--once", expect=5)
    ok("another watcher" in out and "pairtalk status demo" not in out, "a second watcher is refused (exit 5)")
    ok("watcher running" in pt("status") and "running, pid" in pt("status", "demo"), "status shows the running watcher")
    pt("watch", "demo", "--once", "--takeover", expect=1)
    w.wait(timeout=10)
    ok(w.returncode != 0 and not lock.exists(), "--takeover stops the other watcher and releases the lock")

    print("seed")
    standin = TMP / "seed_visual_standin.py"
    standin.write_text(SEED_STANDIN)
    env = dict(ENV, PAIRTALK_SEED_VISUAL=str(standin))
    pptx = TMP / "past" / "seminar.pptx"
    pptx.parent.mkdir(parents=True)
    make_pptx(pptx, ["Good morning. Let me start with a puzzle you have all seen.",
                     "Here is the model.\nIt has two parts.",
                     "",
                     "To wrap up: three things to remember. Thank you."])
    script = TMP / "past" / "SCRIPT.md"
    script.write_text("# Old talk\n\n## Opening\n\nWelcome, everyone. Today is about one idea.\n\n## Middle\n\nThe idea, in one picture.\n\n"
                      "## End\n\nThat is all. Thanks.\n")
    out = pt("seed", str(pptx), str(script), str(TALK), "--duration", "10", "--note", "three past talks", env=env)
    sid = re.search(r"seed (\d{8}-\d{6}-[0-9a-f]{4})", out).group(1)
    sd = DATA / "vault" / "seed" / sid
    ok(all((sd / f).exists() for f in ("manifest.json", "stats.json", "samples.md", "script.json", "seed.json")) and list((sd / "pages").glob("*.png")),
       "seed stores the visual extraction and the talk extraction in vault/seed/<id>/")
    st = json.loads((sd / "stats.json").read_text())
    ok("palette" in st and st["talk"]["talks"] == 3, "stats.json keeps the visual stats and adds the talk stats")
    talks = {t["file"]: t for t in json.loads((sd / "script.json").read_text())["talks"]}
    sem = talks["seminar.pptx"]
    ok(sem["slides"] == 4 and sem["slides_with_notes"] == 3 and sem["total_words"] == 29, "speaker notes come out of the .pptx (slide numbers left out)")
    ok(sem["words_per_minute"] == round(29 / 10) and talks["SCRIPT.md"]["slides"] == 3 and talks["demo"]["format"] == "pairtalk deck",
       "--duration gives words per minute; a SCRIPT.md and a PairTalk folder are read too")
    samples = (sd / "samples.md").read_text()
    ok("Titles and text" in samples and "# Speaker scripts" in samples and "How it opens" in samples and "puzzle" in samples,
       "samples.md has the slides' text and how each talk opens and closes")
    seeds = [e for e in events() if e["kind"] == "seed"]
    ok(len(seeds) == 3 and all(e["project"] is None and e["seed_id"] == sid for e in seeds), "one seed event per file, with no project")
    ok(sid in pt("seed", "--list"), "seed --list shows it")
    ok(len(re.findall(r"^### ", pt("learn", "--all"), re.M)) == 3, "learn --all shows the seed events")
    top = max(int(e["id"][1:]) for e in events())
    pt("seed", "--forget", sid)
    ok(not sd.exists() and not [e for e in events() if e["kind"] == "seed"], "seed --forget removes the seed and its events")
    out = pt("seed", str(script), env=env)
    nid = int(re.search(r"\(E(\d+)", out).group(1))
    ok(nid > top, "event ids are never reused after a forget")
    pt("seed", str(TMP / "nothing-here"), expect=1)
    real = APP.parent / "shared" / "seed_visual.py"
    if real.exists():
        out = pt("seed", str(pptx), "--duration", "10", timeout=600)
        sd = DATA / "vault" / "seed" / re.search(r"seed (\d{8}-\d{6}-[0-9a-f]{4})", out).group(1)
        st = json.loads((sd / "stats.json").read_text())
        ok("palette" in st and st.get("slides_with_notes") == 3 and st["talk"]["per_talk"][0]["words_per_minute"] == 3,
           "with the suite's own shared/seed_visual.py, the visual and the talk extraction share one seed")
    else:
        print("  --  shared/seed_visual.py not found: the stand-in alone was used")

    print("the shared site (a stand-in for Wrangler and D1)")
    fake = TMP / "fake_wrangler.py"
    fake.write_text(FAKE_WRANGLER)
    fake.chmod(0o755)
    d1 = TMP / "d1.sqlite"
    db = sqlite3.connect(d1)
    db.executescript((APP / "cloudflare" / "schema.sql").read_text())
    db.execute("INSERT INTO comments (cid, deck, n, k, sid, title, author, text, created, box) VALUES "
               "('0mhxyz123-0a0b0c0d', 'demo', 8, 2, 'CONVERGE', '', 'Ada Lovelace', 'Label the dashed line in words.', '2026-11-01T10:00:00Z', "
               "'{\"x\":1300,\"y\":300,\"w\":400,\"h\":120}')")
    db.execute("INSERT INTO comment_images (cid, i, mime, w, h, bytes, data) VALUES ('0mhxyz123-0a0b0c0d', 0, 'image/png', 1, 1, ?, ?)",
               (len(PNG), PNG))
    db.execute("INSERT INTO comments (cid, deck, n, k, sid, title, author, text, created, box) VALUES "
               "('0mhxyz124-0a0b0c0e', 'demo', 9, 0, 'RANKING', '', '', 'Always show the in-link counts.', '2026-11-01T10:01:00Z', '')")
    db.execute("INSERT INTO comments (cid, deck, n, k, sid, title, author, text, created, box) VALUES "
               "('0mhxyz125-0a0b0c0f', 'other', 1, 0, 'X', '', '', 'another talk', '2026-11-01T10:02:00Z', '')")
    thanks = script_text("THANKS.0")
    db.execute("INSERT INTO script_edits (eid, deck, sid, k, text, sent, orig, updated, status, author) VALUES "
               "('demo|THANKS|0', 'demo', 'THANKS', 0, 'Thank you. Questions are welcome.', 'Thank you. Questions are welcome.', ?, "
               "'2026-11-01T10:03:00.000Z', 'open', 'Ada Lovelace')", (thanks,))
    db.commit()
    db.close()
    renv = dict(ENV, PAIRTALK_WRANGLER=str(fake), FAKE_D1=str(d1), FAKE_WRANGLER_LOG=str(TMP / "wrangler.log"))
    cfg = TMP / "my.wrangler.toml"
    cfg.write_text('name = "test-site"\npages_build_output_dir = "./site"\n\n[[d1_databases]]\nbinding = "COMMENTS_DB"\n'
                   'database_name = "pairtalk-comments"\ndatabase_id = "00000000-0000-0000-0000-000000000000"\n')
    pt("remote", "demo", "--config", str(cfg), "--pages-project", "test-site", env=renv)
    before = len(events())
    out = pt("watch", "demo", "--remote", "--once", env=renv)
    ok("0mhxyz123-0a0b0c0d" in out and "0mhxyz124-0a0b0c0e" in out and "another talk" not in out, "watch --remote lists this talk's open comments")
    ok("by Ada Lovelace (owner)" in out and "by (no name) (coauthor" in out, "an unnamed comment on the shared site is not the owner's")
    att = re.search(r"Attachment: (\S+)", out)
    ok(att and Path(att.group(1)).read_bytes() == PNG and str(DATA) in att.group(1), "attachments are saved in the data home")
    ok("THANKS.0 · by Ada Lovelace (owner) · in the browser" in out, "watch --remote lists the shared script edits")
    new = events()[before:]
    ok(not any("in-link counts" in json.dumps(e) for e in new) and any(e.get("sid") == "THANKS" and e["via"] == "browser" for e in new),
       "only the named owner's remote edits are evidence")
    log = [json.loads(x) for x in (TMP / "wrangler.log").read_text().splitlines()]
    ok(all("--remote" in a and str(cfg) in a for a in log), "remote reads use --remote and the author's own config")
    pt("resolve", "demo", "0mhxyz123-0a0b0c0d", "The dashed line is labelled 'guarantee'.", "--remote", env=renv)
    row = sqlite3.connect(d1).execute("SELECT status, reply FROM comments WHERE cid = '0mhxyz123-0a0b0c0d'").fetchone()
    ok(row[0] == "done" and row[1].startswith("The dashed line"), "resolve --remote writes the reply to D1")
    out = pt("script", "apply", "demo", "--remote", env=renv)
    ok("Questions are welcome" in (TALK / "slides" / "11_thanks.js").read_text(), "script apply --remote writes the shared edit into the slide")
    ok(sqlite3.connect(d1).execute("SELECT status FROM script_edits").fetchone()[0] == "done", "and closes it in D1")
    pt("snapshot", "demo")
    out = pt("publish", "demo", "--stage", env=renv)
    st = DATA / "projects" / "demo" / "site-build"
    ok((st / "site" / "index.html").exists() and (st / "functions" / "_middleware.js").exists() and (st / "site" / "_routes.json").exists(),
       "publish --stage builds the site in the data home, with the middleware")
    ok('DECK = "demo"' in (st / "wrangler.toml").read_text() and "00000000-0000" in (st / "wrangler.toml").read_text(),
       "the staged config is the author's own, with the talk's name")
    ok(not (APP / "cloudflare" / "site").exists(), "nothing is staged in the code folder")

    print("screenshots and the bundle")
    chrome = os.environ.get("CHROME_PATH") or next((c for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                                                               "/usr/bin/google-chrome", "/usr/bin/chromium") if Path(c).exists()), None)
    if chrome and (APP / "node_modules" / "playwright").exists():
        out = pt("shots", "demo", "--ids", "SHARE", "--click", "1", "--box", "700,740,520,110", timeout=300)
        man = json.loads((DATA / "projects" / "demo" / "shots" / "manifest.json").read_text())
        ok(man["ok"] and len(man["captures"]) == 1 and man["box"], "shots captures one click with the comment's box")
        pt("bundle", "demo", timeout=300)
        html = (TALK / "dist" / "demo.html").read_text()
        ok(len(html) > 500_000 and "How PageRank" in html, "bundle writes one offline HTML file")
    else:
        print("  --  no Chrome or Playwright: screenshots skipped")

    print("the shared site's middleware (offline)")
    r = subprocess.run(["node", str(APP / "cloudflare" / "tests" / "smoke.mjs")], capture_output=True, text=True)
    ok(r.returncode == 0 and "assertions passed" in r.stdout, r.stdout.strip() or r.stderr.strip())

    print(f"\nall {passed} checks passed")
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
