#!/usr/bin/env python3
"""End-to-end test of PairPoster: setup, new, qa, print, the review server, watch, resolve, learn.

Everything runs in a temporary HOME and data home; nothing outside them is touched. The measured checks, screenshots and
printing run only when Chrome or Chromium is found.
Run: python3 tests/test_e2e.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

PP = Path(__file__).resolve().parent.parent / "bin" / "pairposter"
PD = Path(__file__).resolve().parent.parent.parent / "pairdeck" / "bin" / "pairdeck"
TMP = Path(tempfile.mkdtemp(prefix="pairposter-test-"))
HOME = TMP / "home"
DATA = TMP / "data"
ENV = dict(os.environ, HOME=str(HOME), PAIRPOSTER_HOME=str(DATA), GIT_TERMINAL_PROMPT="0",
           GIT_CONFIG_GLOBAL=str(TMP / "gitconfig"), GIT_CONFIG_NOSYSTEM="1")
ENV.pop("PAIRLAB_FLAVOR", None)
POSTER_DIR = TMP / "posters" / "demo"
passed = 0
procs: list = []


def run(tool, *args, expect=0, timeout=300):
    r = subprocess.run([sys.executable, str(tool), *args], env=ENV, capture_output=True, text=True, timeout=timeout)
    if expect is not None and r.returncode != expect:
        raise AssertionError(f"{tool.name} {' '.join(args)}: exit {r.returncode}, expected {expect}\n--- stdout\n{r.stdout}\n"
                             f"--- stderr\n{r.stderr}")
    return r.stdout + r.stderr


def pp(*args, **kw):
    return run(PP, *args, **kw)


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
                                                 shutil.which("google-chrome"), shutil.which("chromium"),
                                                 shutil.which("chromium-browser")])


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    HOME.mkdir(parents=True)
    (TMP / "gitconfig").write_text("[user]\n\tname = Test\n\temail = test@example.com\n")

    print("cli")
    out = pp("--version")
    ok(out.strip() == "pairposter 0.1.0", "pairposter --version names the poster flavour")
    out = pp("--help")
    ok(" print " in out or "print," in out, "the help lists print")
    cmds = set(re.search(r"\{([a-z,]+)\}", out).group(1).split(","))
    ok("print" in cmds and not cmds & {"bundle", "card"}, "the deck-only commands are not offered")
    ok(run(PD, "--version").strip().startswith("pairdeck 0.1"), "pairdeck itself still runs as PairDeck")

    print("setup")
    out = pp("setup", "--name", "Ada Lovelace")
    ok((DATA / "profile.json").exists(), "setup writes the profile")
    style = (DATA / "vault" / "STYLE.md").read_text()
    ok("poster style: the living guide" in style, "the vault starts from the poster template")
    log = subprocess.run(["git", "-C", str(DATA), "log", "--format=%s"], capture_output=True, text=True, env=ENV).stdout
    ok("PairPoster data home" in log, "the data home is a git repository")
    out = pp("paths")
    ok("visual look" in out and ".pairdeck" in out, "paths names PairDeck's guide as the visual look")

    print("new")
    pp("new", "demo", "--title", "A Demo Poster|With a subtitle", "--size", "1400x900", "--dir", str(POSTER_DIR))
    page = (POSTER_DIR / "index.html").read_text()
    ok('"width_mm": 1400, "height_mm": 900' in page, "the page size is in the meta tag")
    ok((POSTER_DIR / "_poster" / "poster.css").exists() and (POSTER_DIR / "_poster" / "mathjax").is_dir(),
       "the engine and MathJax are copied next to the poster")
    ok('<symbol id="trend-down"' in page and "{{" not in page, "the icon sprite is inlined and no placeholder is left")
    ok("TODO: authors" in page, "the authors line replaces the deck's subtitle default")
    out = pp("new", "bad", "--title", "X", "--size", "huge", "--dir", str(TMP / "bad"), expect=1)
    ok("WIDTHxHEIGHT" in out, "a malformed size is refused")
    out = pp("qa", "demo", "--no-shots")
    ok("1400 x 900 mm" in out and "lint: clean" in out, "qa --no-shots checks the page statically")
    broken = TMP / "broken.html"
    broken.write_text("<html><body>no poster</body></html>")
    out = pp("qa", str(broken), "--no-shots", expect=1)
    ok("pp-poster" in out and "ERROR" in out, "a page without the skeleton is an error")

    if have_chrome():
        print("qa and print (Chrome)")
        out = pp("qa", "demo", expect=1)
        ok("TODO left on the poster" in out and "Words:" in out, "qa measures the template and flags its TODOs")
        shots = sorted(p.name for p in (DATA / "projects" / "demo" / "qa").glob("*.png"))
        ok("poster.png" in shots and len([s for s in shots if s.startswith("close-")]) == 6,
           "qa writes the whole poster and six close-ups")
        # fill the template: no TODO, short phrases
        filled = re.sub(r"TODO: ?", "", page).replace(">TODO<", ">42<").replace("TODO", "42")
        filled = filled.replace("the one formula worth a glance", "x+y")
        (POSTER_DIR / "index.html").write_text(filled)
        out = pp("qa", "demo", expect=None)
        ok("TODO" not in out.split("Screenshots")[0] and "overflow" not in out, "a filled poster has no TODO and no overflow")
        tall = filled.replace('<p class="pp-lead">', '<p class="pp-lead">' + "word " * 400, 1)
        (POSTER_DIR / "index.html").write_text(tall)
        out = pp("qa", "demo", expect=1)
        ok("overflow: [Question]" in out, "qa reports a block that overflows, by its label")
        ok(re.search(r"words: \[Question\] has \d+ words", out) is not None, "qa reports a block over its word budget")
        (POSTER_DIR / "index.html").write_text(filled)
        out = pp("print", "demo")
        pdf = POSTER_DIR / "print" / "demo.pdf"
        ok(pdf.exists() and "1 page(s) · 1400 x 900 mm" in out, "print writes a one-page PDF at the poster's size")
        png = POSTER_DIR / "print" / "demo_4480x2880.png"
        ok(png.exists() and png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "print writes the PNG at 4480 x 2880")
        w, h = int.from_bytes(png.read_bytes()[16:20], "big"), int.from_bytes(png.read_bytes()[20:24], "big")
        ok((w, h) == (4480, 2880), "the PNG has the requested pixel size")
    else:
        print("  (no Chrome: skipped the measured checks and printing)")

    print("the comment loop")
    pp("snapshot", "demo", "-m", "first build")
    port = free_port()
    p = subprocess.Popen([sys.executable, str(PP), "review", "demo", "--port", str(port)], env=ENV,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    procs.append(p)
    url = f"http://127.0.0.1:{port}/index.html"
    for _ in range(50):
        try:
            html = urllib.request.urlopen(url, timeout=2).read().decode()
            break
        except OSError:
            time.sleep(0.1)
    ok('"unit": "poster"' in html and '"cli": "pairposter"' in html and "pp-block" in html,
       "the review page injects the overlay in its poster mode")
    body = json.dumps({"text": "Bigger numbers, and always a unit under a big number.", "box": {"x": .7, "y": .15, "w": .25, "h": .12},
                       "block": "Results", "under": "42 · what the number is", "slide": 1}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{port}/__pairdeck/comments", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{port}"})
    rec = json.loads(urllib.request.urlopen(req, timeout=5).read())
    ok(rec.get("id") == "c1" and rec.get("block") == "Results", "a comment is stored with the block it points at")
    out = pp("watch", "demo", "--once", "--settle", "0")
    ok("# PairPoster · demo" in out and '## c1 · block "Results"' in out, "the watcher's batch names the poster and the block")
    ok("fractions of the poster" in out and "pairposter resolve demo" in out, "the batch speaks of the poster and its CLI")
    ok("stated · c1" in out, "a comment written as a rule becomes stated evidence")
    pp("resolve", "demo", "c1", "Both numbers are now 96 pt with their units under them.")
    state = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/__pairdeck/state", timeout=5).read())
    ok(state["comments"][0]["status"] == "answered", "the reply reaches the review page")
    out = pp("learn", "demo", "--json")
    ok('"kind": "stated"' in out, "learn shows the pending evidence")
    p.terminate()
    p.wait(timeout=10)
    out = pp("status")
    ok("demo:" in out and "visual look:" in out, "status lists the poster and the visual-look guide")

    print("figdata")
    # a synthetic figure in matplotlib's PDF idiom: grid lines, tick marks, tick labels, a band and a line, a legend sample
    ops = ["/DeviceRGB CS", "/DeviceRGB cs"]
    X = lambda v: 50 + v * 40          # noqa: E731  (x = 0..4)
    Y = lambda v: 40 + v * 100         # noqa: E731  (y = 0..1)
    for v in range(5):
        ops += [f"{X(v)} 40 m", f"{X(v)} 140 l", "S", f"{X(v)} 40 m", f"{X(v)} 35 l", "B",
                f"BT /F1 10 Tf {X(v) - 3} 22 Td ({v}) Tj ET"]
    for v in (0, 0.5, 1):
        ops += [f"50 {Y(v)} m", f"210 {Y(v)} l", "S", f"50 {Y(v)} m", f"45 {Y(v)} l", "B",
                f"BT /F1 10 Tf 25 {Y(v) - 3.6} Td ({v:g}) Tj ET"]
    ys = [0.1, 0.4, 0.55, 0.62, 0.7]
    ops += ["0.2 0.4 0.8 rg", f"{X(0)} {Y(ys[0] + .05)} m"]
    ops += [f"{X(i)} {Y(y - .05)} l" for i, y in enumerate(ys)] + [f"{X(i)} {Y(y + .05)} l" for i, y in reversed(list(enumerate(ys)))]
    ops += ["h", "f", "0.2 0.4 0.8 RG", f"{X(0)} {Y(ys[0])} m"] + [f"{X(i)} {Y(y)} l" for i, y in enumerate(ys[1:], 1)] + ["S"]
    ops += ["q 1 0 0 1 170 120 cm", "0 0 m", "5 0 l", "10 0 l", "S", "BT /F1 9 Tf 14 0 Td (1) Tj ET", "Q"]
    body = "\n".join(ops).encode()
    pdf = TMP / "fig.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj << /Length " + str(len(body)).encode() + b" >>\nstream\n" + body
                    + b"\nendstream\nendobj\n%%EOF\n")
    fd = Path(__file__).resolve().parent.parent / "tools" / "figdata.py"
    r = subprocess.run([sys.executable, str(fd), str(pdf)], capture_output=True, text=True, timeout=60)
    data = json.loads(r.stdout) if r.returncode == 0 else {}
    ser = data.get("series", [])
    ok(len(ser) == 1, "figdata finds the one data line (not the grid, the ticks or the legend sample)")
    ok(ser and max(abs(a - b) for a, b in zip(ser[0]["y"], ys)) < 1e-6 and ser[0]["x"] == [0, 1, 2, 3, 4],
       "figdata recovers the line's values through the axis mapping")
    ok(ser and ser[0]["lo"] and max(abs(a - (b - .05)) for a, b in zip(ser[0]["lo"], ys)) < 1e-6,
       "figdata recovers the error band of the same colour")

    print(f"\nall {passed} checks passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
        shutil.rmtree(TMP, ignore_errors=True)
