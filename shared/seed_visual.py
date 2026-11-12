#!/usr/bin/env python3
"""seed_visual.py: read an author's past decks or talks into one seed folder of a PairLab style vault.

Usage:
  python3 shared/seed_visual.py PATH... --out DIR [--max-pages N] [--kind deck|talk] [--json]

PATH may be files or folders (searched recursively, hidden folders skipped):
  .pptx         theme colours and fonts, per-slide text and titles, speaker notes, layout names, picture/chart/table counts,
                colours and fonts used on the slides; page images when LibreOffice (soffice) can export a PDF
  .pdf          sampled page images (macOS PDFKit through swift, else pdftoppm, else mutool), palette from the pixels,
                fonts named in the file, text per page (pdftotext if present, else PDFKit)
  .html, .htm   CSS custom properties, colours (with how often each is used), font families, slides (<section> or
                elements whose class names a slide), slide text, titles, notes (<aside class="notes">, data-notes), builds
  .md           with --kind talk only: a talk script (words, sections)
  .key          skipped: export from Keynote to PDF or PPTX first

Writes into DIR (created if needed): manifest.json (file, sha256, format, pages, images), stats.json (palette with
frequencies, fonts, slide count, words per slide, titles, notes length, layouts), samples.md (titles and text per slide,
notes when present) and pages/<stem>-NN.png. Never modifies or uploads the inputs. Prints a short summary, or JSON with --json.

PairDeck and PairTalk both call this script; keep its interface stable. Standard library only (Python 3.9+).
"""

from __future__ import annotations

import argparse
import collections
import colorsys
import datetime as dt
import hashlib
import html as htmlmod
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

VERSION = "1.0"
FORMATS = {".pptx": "pptx", ".pdf": "pdf", ".html": "html", ".htm": "html", ".key": "key", ".md": "md"}

# ------------------------------------------------------------------------------------------------ helpers


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def words(text: str) -> int:
    return len(re.findall(r"[\w’'-]+", text or "")) + len(re.findall(r"[一-鿿]", text or ""))


def clip(text: str, n: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def hex6(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def parse_colour(s: str) -> str | None:
    """A CSS or OOXML colour as #RRGGBB, or None (transparent, keywords other than black and white, bad syntax)."""
    s = s.strip()
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?", s)
    if m:
        return "#" + m.group(1).upper()
    m = re.fullmatch(r"#([0-9a-fA-F]{3})[0-9a-fA-F]?", s)
    if m:
        return "#" + "".join(c * 2 for c in m.group(1)).upper()
    m = re.fullmatch(r"rgba?\(\s*([\d.]+%?)[\s,]+([\d.]+%?)[\s,]+([\d.]+%?)(?:[\s,/]+([\d.]+%?))?\s*\)", s)
    if m:
        def ch(v):
            return round(float(v[:-1]) * 2.55) if v.endswith("%") else round(float(v))
        if m.group(4) is not None:
            a = float(m.group(4)[:-1]) / 100 if m.group(4).endswith("%") else float(m.group(4))
            if a < 0.5:
                return None
        return hex6(*(max(0, min(255, ch(m.group(i)))) for i in (1, 2, 3)))
    m = re.fullmatch(r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:[\s,/]+([\d.]+%?))?\s*\)", s)
    if m:
        r, g, b = colorsys.hls_to_rgb(float(m.group(1)) / 360, float(m.group(3)) / 100, float(m.group(2)) / 100)
        return hex6(round(r * 255), round(g * 255), round(b * 255))
    return {"white": "#FFFFFF", "black": "#000000"}.get(s.lower())


def role_hint(hexc: str) -> str:
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.18 or l > 0.94 or l < 0.08:
        return "light neutral" if l > 0.8 else "dark neutral" if l < 0.25 else "neutral"
    return "accent"


def summarize(values: list) -> dict:
    if not values:
        return {}
    v = sorted(values)
    return {"mean": round(statistics.mean(v), 1), "median": statistics.median(v), "p90": v[min(len(v) - 1, int(0.9 * len(v)))],
            "max": v[-1], "min": v[0]}


def sample_pages(n: int, k: int) -> list[int]:
    if n <= k:
        return list(range(1, n + 1))
    if k <= 1:
        return [1]
    return sorted({round(i * (n - 1) / (k - 1)) + 1 for i in range(k)})


# ------------------------------------------------------------------------------------------------ PNG pixels (palette)

def png_pixels(path: Path):
    """(width, height, list of (r, g, b)) for an 8-bit, non-interlaced PNG, or None. Small images only (palette)."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, plte = 8, [], None
    w = h = depth = ctype = interlace = 0
    while pos + 8 <= len(data):
        n = int.from_bytes(data[pos:pos + 4], "big")
        kind, chunk = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            w, h = int.from_bytes(chunk[0:4], "big"), int.from_bytes(chunk[4:8], "big")
            depth, ctype, interlace = chunk[8], chunk[9], chunk[12]
        elif kind == b"PLTE":
            plte = [tuple(chunk[i:i + 3]) for i in range(0, len(chunk), 3)]
        elif kind == b"IDAT":
            idat.append(chunk)
        elif kind == b"IEND":
            break
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if depth != 8 or interlace or not bpp or w * h > 600_000:
        return None
    import zlib
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    prev = bytearray(stride)
    px = []
    i = 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        for x in range(0, stride, bpp):
            if ctype == 6:
                if line[x + 3] < 128:
                    continue
                px.append((line[x], line[x + 1], line[x + 2]))
            elif ctype == 2:
                px.append((line[x], line[x + 1], line[x + 2]))
            elif ctype == 3 and plte:
                px.append(plte[line[x]])
            elif ctype in (0, 4):
                if ctype == 4 and line[x + 1] < 128:
                    continue
                px.append((line[x],) * 3)
        prev = line
    return w, h, px


def merge_close(counter: collections.Counter, tol: int = 6, floor: float = 0.004) -> collections.Counter:
    """Fold colours within `tol` per channel into the heaviest nearby one (anti-aliasing, #2E75B5 vs #2E75B6), and drop
    colours under `floor` of the total (edge pixels)."""
    kept: list = []
    out = collections.Counter()
    total = sum(counter.values()) or 1
    for h, c in counter.most_common():
        rgb = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        for k, krgb in kept:
            if max(abs(a - b) for a, b in zip(rgb, krgb)) <= tol:
                out[k] += c
                break
        else:
            kept.append((h, rgb))
            out[h] += c
    return collections.Counter({h: c for h, c in out.items() if c / total >= floor})


def pixel_palette(pixels: list) -> collections.Counter:
    """Colour shares from pixels, binned to 4 bits per channel and reported as each bin's mean colour."""
    bins: dict = {}
    for r, g, b in pixels:
        k = (r >> 4, g >> 4, b >> 4)
        s = bins.setdefault(k, [0, 0, 0, 0])
        s[0] += r
        s[1] += g
        s[2] += b
        s[3] += 1
    out = collections.Counter()
    for s in bins.values():
        out[hex6(s[0] // s[3], s[1] // s[3], s[2] // s[3])] += s[3]
    return out


# ------------------------------------------------------------------------------------------------ PDF rendering

SWIFT_PAGES = r"""
import AppKit
import Foundation
import PDFKit
// args: pdf, bigDir, smallDir, stem, pages (comma list or ""), bigWidth, smallWidth, wantText (0/1)
let a = CommandLine.arguments
guard a.count >= 9, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else {
    FileHandle.standardError.write("cannot open the PDF\n".data(using: .utf8)!); exit(1)
}
let want = a[5].split(separator: ",").compactMap { Int($0) }
let bigW = Int(a[6]) ?? 1280, smallW = Int(a[7]) ?? 240
func render(_ page: PDFPage, _ width: Int) -> Data? {
    let box = page.bounds(for: .mediaBox)
    if box.width <= 0 || box.height <= 0 { return nil }
    let h = max(1, Int((CGFloat(width) * box.height / box.width).rounded()))
    guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: h, bitsPerSample: 8,
                                     samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                                     bytesPerRow: 0, bitsPerPixel: 0),
          let ctx = NSGraphicsContext(bitmapImageRep: rep) else { return nil }
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = ctx
    let cg = ctx.cgContext
    cg.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    cg.fill(CGRect(x: 0, y: 0, width: width, height: h))
    cg.scaleBy(x: CGFloat(width) / box.width, y: CGFloat(h) / box.height)
    cg.translateBy(x: -box.origin.x, y: -box.origin.y)
    page.draw(with: .mediaBox, to: cg)
    NSGraphicsContext.restoreGraphicsState()
    return rep.representation(using: .png, properties: [:])
}
var texts: [String] = []
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { texts.append(""); continue }
    texts.append(a[8] == "1" ? (page.string ?? "") : "")
    if want.contains(i + 1) {
        let name = String(format: "%@-%02d.png", a[4], i + 1)
        if let d = render(page, bigW) { try? d.write(to: URL(fileURLWithPath: a[2] + "/" + name)) }
        if let d = render(page, smallW) { try? d.write(to: URL(fileURLWithPath: a[3] + "/" + name)) }
    }
}
let out: [String: Any] = ["pages": doc.pageCount, "text": texts]
let data = try! JSONSerialization.data(withJSONObject: out, options: [])
FileHandle.standardOutput.write(data)
"""


def pdf_page_count(path: Path) -> int:
    if shutil.which("pdfinfo"):
        r = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
        m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M)
        if m:
            return int(m.group(1))
    data = path.read_bytes()
    counts = [int(x) for x in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page\b(?!s)", data))


def pdf_fonts(path: Path) -> collections.Counter:
    """Font names the PDF embeds or references (subset prefixes removed), from raw and compressed objects."""
    import zlib
    data = path.read_bytes()
    found = collections.Counter()
    chunks = [data]
    for m in re.finditer(rb"stream\r?\n", data):
        if len(chunks) > 3000:
            break
        start = m.end()
        end = data.find(b"endstream", start)
        if end < 0 or end - start > 4_000_000:
            continue
        try:
            chunks.append(zlib.decompress(data[start:end]))
        except zlib.error:
            pass
    for c in chunks:
        for name in re.findall(rb"/BaseFont\s*/([A-Za-z0-9+\-_,.#]+)", c):
            n = name.decode("latin-1")
            n = re.sub(r"^[A-Z]{6}\+", "", n).replace("#20", " ")
            found[n] += 1
    return found


class PdfRenderer:
    """Page images and text for a PDF: macOS PDFKit (through swift), else pdftoppm, else mutool; text from pdftotext,
    else PDFKit."""

    def __init__(self):
        self.swift = shutil.which("swift") if sys.platform == "darwin" else None
        self.pdftoppm = shutil.which("pdftoppm")
        self.mutool = shutil.which("mutool")
        self.pdftotext = shutil.which("pdftotext")
        self.name = "pdfkit" if self.swift else "pdftoppm" if self.pdftoppm else "mutool" if self.mutool else "none"
        self._script = None

    def script(self) -> str:
        if not self._script:
            fd, self._script = tempfile.mkstemp(suffix=".swift", prefix="seed-pages-")
            with os.fdopen(fd, "w") as f:
                f.write(SWIFT_PAGES)
        return self._script

    def close(self):
        if self._script and os.path.exists(self._script):
            os.unlink(self._script)

    def run(self, pdf: Path, big: Path, small: Path, stem: str, max_pages: int) -> dict:
        """{"pages": n, "text": [per page], "images": [big PNG paths], "small": [small PNG paths], "how": renderer}."""
        res = {"pages": 0, "text": [], "images": [], "small": [], "how": self.name, "text_how": "none"}
        swift_out = None
        if self.swift:
            n_guess = max(1, pdf_page_count(pdf))
            want = sample_pages(n_guess, max_pages)
            r = subprocess.run([self.swift, self.script(), str(pdf), str(big), str(small), stem, ",".join(map(str, want)),
                                "1280", "240", "0" if self.pdftotext else "1"],
                               capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                try:
                    swift_out = json.loads(r.stdout)
                except ValueError:
                    swift_out = None
            if swift_out:
                res["pages"] = swift_out["pages"]
                if swift_out["pages"] != n_guess:  # sample again on the true count (rare: the guess was off)
                    want2 = sample_pages(swift_out["pages"], max_pages)
                    if set(want2) - set(want):
                        subprocess.run([self.swift, self.script(), str(pdf), str(big), str(small), stem,
                                        ",".join(map(str, want2)), "1280", "240", "0"], capture_output=True, timeout=600)
                if not self.pdftotext:
                    res["text"], res["text_how"] = swift_out["text"], "pdfkit"
            else:
                res["how"] = "pdftoppm" if self.pdftoppm else "mutool" if self.mutool else "none"
        if not swift_out:
            res["pages"] = pdf_page_count(pdf)
            for n in sample_pages(res["pages"], max_pages):
                name = f"{stem}-{n:02d}"
                if res["how"] == "pdftoppm":
                    for d, wd in ((big, 1280), (small, 240)):
                        subprocess.run([self.pdftoppm, "-f", str(n), "-l", str(n), "-png", "-singlefile", "-scale-to-x",
                                        str(wd), "-scale-to-y", "-1", str(pdf), str(d / name)],
                                       capture_output=True, timeout=300)
                elif res["how"] == "mutool":
                    for d, wd in ((big, 1280), (small, 240)):
                        subprocess.run([self.mutool, "draw", "-q", "-w", str(wd), "-o", str(d / (name + ".png")), str(pdf),
                                        str(n)], capture_output=True, timeout=300)
        if self.pdftotext:
            r = subprocess.run([self.pdftotext, "-layout", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, timeout=300)
            pages = r.stdout.decode("utf-8", "replace").split("\f")
            res["text"], res["text_how"] = pages[: res["pages"]] if res["pages"] else pages, "pdftotext"
        res["images"] = sorted(str(p) for p in big.glob(f"{glob_escape(stem)}-*.png"))
        res["small"] = sorted(str(p) for p in small.glob(f"{glob_escape(stem)}-*.png"))
        return res


def glob_escape(s: str) -> str:
    return re.sub(r"([*?\[\]])", r"[\1]", s)


# ------------------------------------------------------------------------------------------------ .pptx

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
RELS = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
R_ID = "{%s}id" % NS["r"]


def _rels(z: zipfile.ZipFile, part: str) -> dict:
    """Relationships of a part: id -> (type suffix, absolute target path inside the zip)."""
    d, f = os.path.split(part)
    rel_path = f"{d}/_rels/{f}.rels"
    if rel_path not in z.namelist():
        return {}
    out = {}
    for r in ET.fromstring(z.read(rel_path)).iter(RELS):
        target = r.get("Target", "")
        if r.get("TargetMode") == "External":
            continue
        full = os.path.normpath(os.path.join(d, target)).replace(os.sep, "/") if not target.startswith("/") else target[1:]
        out[r.get("Id")] = (r.get("Type", "").rsplit("/", 1)[-1], full)
    return out


def _paras(el) -> list[str]:
    out = []
    for p in el.iter("{%s}p" % NS["a"]):
        t = "".join(x.text or "" for x in p.iter("{%s}t" % NS["a"])).strip()
        if t:
            out.append(t)
    return out


def read_pptx(path: Path) -> dict:
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    prels = _rels(z, "ppt/presentation.xml")
    size = pres.find("p:sldSz", NS)
    aspect = None
    if size is not None:
        cx, cy = int(size.get("cx", 0)), int(size.get("cy", 0))
        if cx and cy:
            aspect = "16:9" if abs(cx / cy - 16 / 9) < 0.02 else "4:3" if abs(cx / cy - 4 / 3) < 0.02 else f"{cx / cy:.2f}:1"
    order = [prels[s.get(R_ID)][1] for s in pres.iterfind("p:sldIdLst/p:sldId", NS) if s.get(R_ID) in prels]
    # the theme of the first slide master
    theme_part = "ppt/theme/theme1.xml"
    for _, (kind, target) in prels.items():
        if kind == "slideMaster":
            for _, (k2, t2) in _rels(z, target).items():
                if k2 == "theme":
                    theme_part = t2
            break
    theme_colours, major, minor = {}, None, None
    if theme_part in names:
        th = ET.fromstring(z.read(theme_part))
        scheme = th.find(".//a:clrScheme", NS)
        if scheme is not None:
            for slot in scheme:
                tag = slot.tag.split("}")[-1]
                c = slot.find("a:srgbClr", NS)
                s = slot.find("a:sysClr", NS)
                val = c.get("val") if c is not None else s.get("lastClr") if s is not None else None
                if val:
                    theme_colours[tag] = "#" + val.upper()
        mj = th.find(".//a:majorFont/a:latin", NS)
        mn = th.find(".//a:minorFont/a:latin", NS)
        major = mj.get("typeface") if mj is not None else None
        minor = mn.get("typeface") if mn is not None else None
    scheme_map = dict(theme_colours)
    scheme_map.update({"tx1": theme_colours.get("dk1"), "bg1": theme_colours.get("lt1"), "tx2": theme_colours.get("dk2"),
                       "bg2": theme_colours.get("lt2")})
    colours, fonts, sizes, layouts = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    slides, pictures, charts, tables = [], 0, 0, 0
    for n, part in enumerate(order, 1):
        if part not in names:
            continue
        x = ET.fromstring(z.read(part))
        rels = _rels(z, part)
        title, body = "", []
        for sp in x.iter("{%s}sp" % NS["p"]):
            ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
            text = _paras(sp)
            if ph is not None and ph.get("type") in ("title", "ctrTitle") and not title:
                title = " ".join(text)
            elif ph is not None and ph.get("type") in ("sldNum", "dt", "ftr"):
                continue
            else:
                body += text
        for tbl in x.iter("{%s}tbl" % NS["a"]):
            tables += 1
            body += _paras(tbl)
        pictures += sum(1 for _ in x.iter("{%s}pic" % NS["p"]))
        for gd in x.iter("{%s}graphicData" % NS["a"]):
            if gd.get("uri", "").endswith("/chart"):
                charts += 1
        for c in x.iter("{%s}srgbClr" % NS["a"]):
            colours["#" + c.get("val", "000000").upper()] += 1
        for c in x.iter("{%s}schemeClr" % NS["a"]):
            hexc = scheme_map.get(c.get("val"))
            if hexc:
                colours[hexc] += 1
        for f in x.iter("{%s}latin" % NS["a"]):
            face = f.get("typeface", "")
            face = major if face == "+mj-lt" else minor if face == "+mn-lt" else face
            if face:
                fonts[face] += 1
        for tag in ("rPr", "defRPr"):
            for r in x.iter("{%s}%s" % (NS["a"], tag)):
                if r.get("sz"):
                    sizes[int(r.get("sz")) / 100] += 1
        layout, notes = "", ""
        for kind, target in rels.values():
            if kind == "slideLayout" and target in names:
                cs = ET.fromstring(z.read(target)).find("p:cSld", NS)
                layout = cs.get("name", "") if cs is not None else ""
            elif kind == "notesSlide" and target in names:
                nx = ET.fromstring(z.read(target))
                parts = []
                for sp in nx.iter("{%s}sp" % NS["p"]):
                    ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
                    if ph is not None and ph.get("type") in ("sldNum", "sldImg", "hdr", "ftr", "dt"):
                        continue
                    parts += _paras(sp)
                notes = "\n".join(parts)
        if layout:
            layouts[layout] += 1
        text = "\n".join(body)
        slides.append({"n": n, "title": title, "text": text, "notes": notes, "layout": layout,
                       "words": words(title) + words(text), "notes_words": words(notes)})
    # theme colours count once each, so a deck that only uses the theme still shows its palette
    for hexc in theme_colours.values():
        colours[hexc] += 1
    if major:
        fonts[major] += 1
    if minor:
        fonts[minor] += 1
    return {"slides": slides, "colours": colours, "fonts": fonts, "sizes": sizes, "layouts": layouts,
            "theme": {"colours": theme_colours, "major_font": major, "minor_font": minor}, "aspect": aspect,
            "pictures": pictures, "charts": charts, "tables": tables}


def pptx_to_pdf(path: Path, tmp: Path) -> Path | None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(path)],
                       capture_output=True, timeout=600)
    out = tmp / (path.stem + ".pdf")
    return out if r.returncode == 0 and out.exists() else None


# ------------------------------------------------------------------------------------------------ .html

COLOUR_TOKEN = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)")


def strip_tags(s: str) -> str:
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</(p|li|h\d|div|tspan|text|td|th|tr)>", "\n", s, flags=re.I)
    s = htmlmod.unescape(re.sub(r"<[^>]+>", " ", s))
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def top_level(page: str, open_re: str, tag: str) -> list[tuple[int, int]]:
    """Spans of top-level elements whose opening tag matches open_re (nesting counted on `tag`)."""
    spans, depth, start = [], 0, None
    for m in re.finditer(r"<(/?)%s\b[^>]*>" % tag, page, re.I):
        if not m.group(1):
            if depth == 0:
                if re.match(open_re, m.group(0), re.I):
                    start = m.start()
                else:
                    start = None
            depth += 1
        else:
            depth = max(0, depth - 1)
            if depth == 0 and start is not None:
                spans.append((start, m.end()))
                start = None
    return spans


def read_html(path: Path) -> dict:
    page = path.read_text(encoding="utf-8", errors="replace")
    css_parts = re.findall(r"<style\b[^>]*>(.*?)</style>", page, re.S | re.I)
    linked = []
    for href in re.findall(r'<link\b[^>]*rel=["\']?stylesheet[^>]*href=["\']([^"\']+)["\']', page, re.I) + \
            re.findall(r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']?stylesheet', page, re.I):
        if re.match(r"^(https?:)?//", href):
            linked.append(href)
            continue
        f = (path.parent / href.split("?")[0]).resolve()
        if f.is_file() and f.stat().st_size < 1_500_000:
            css_parts.append(f.read_text(encoding="utf-8", errors="replace"))
    css = "\n".join(css_parts)
    css_nocomment = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    props = {}
    for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;}{]+)", css_nocomment):
        props.setdefault(name, val.strip())
    var_uses = collections.Counter(re.findall(r"var\(\s*(--[\w-]+)", css_nocomment + page))
    colours = collections.Counter()
    for tok in COLOUR_TOKEN.findall(css_nocomment):
        c = parse_colour(tok)
        if c:
            colours[c] += 1
    body = page[page.lower().find("<body"):] if "<body" in page.lower() else page
    body_nostyle = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S | re.I)
    for tok in re.findall(r'(?:fill|stroke|color|background(?:-color)?|stop-color)\s*[:=]\s*["\']?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))',
                          body_nostyle, re.I):
        c = parse_colour(tok)
        if c:
            colours[c] += 1
    for name, n in var_uses.items():  # a custom property's colour counts each time the deck uses it
        c = parse_colour(props.get(name, ""))
        if c:
            colours[c] += n
    fonts = collections.Counter()
    for decl in re.findall(r"font-family\s*:\s*([^;}{]+)", css_nocomment + body_nostyle, re.I):
        fams = [f.strip().strip("\"'") for f in decl.split(",")]
        fams = [f for f in fams if f and not f.startswith("var(")]
        if fams:
            fonts[fams[0]] += 1
    for name, val in props.items():
        if re.search(r"font|serif|sans|mono", name, re.I):
            fams = [f.strip().strip("\"'") for f in val.split(",") if f.strip()]
            if fams and not fams[0].startswith("var("):
                fonts[fams[0]] += 1 + var_uses.get(name, 0)
    for fam in re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"':]+)", page):
        fonts[fam.replace("+", " ")] += 1
    sizes = collections.Counter()
    for v in re.findall(r"font-size\s*:\s*([\d.]+)px", css_nocomment, re.I):
        sizes[float(v)] += 1
    spans = top_level(page, r"<section\b[^>]*class=[\"'][^\"']*slide", "section") or \
        top_level(page, r"<section\b", "section") or \
        top_level(page, r"<div\b[^>]*class=[\"'][^\"']*\bslide\b", "div")
    slides = []
    for n, (a, b) in enumerate(spans or [(0, len(body))], 1):
        chunk = page[a:b] if spans else body
        notes = " ".join(strip_tags(x) for x in re.findall(r"<aside\b[^>]*class=[\"'][^\"']*notes[^\"']*[\"'][^>]*>(.*?)</aside>",
                                                          chunk, re.S | re.I))
        notes += " ".join(htmlmod.unescape(x) for x in re.findall(r'data-notes="([^"]*)"', chunk))
        chunk_wo = re.sub(r"<aside\b[^>]*class=[\"'][^\"']*notes.*?</aside>", " ", chunk, flags=re.S | re.I)
        h = re.search(r"<h[1-3]\b[^>]*>(.*?)</h[1-3]>", chunk_wo, re.S | re.I)
        title = strip_tags(h.group(1)).replace("\n", " ") if h else ""
        text = strip_tags(chunk_wo)
        if title and text.startswith(title):
            text = text[len(title):].lstrip("\n")
        label = re.match(r"<[^>]*data-label=[\"']([^\"']*)", chunk)
        steps = set(re.findall(r'data-step="([^"]+)"', chunk)) | set(range(len(re.findall(r'class="[^"]*\bfragment\b', chunk))))
        slides.append({"n": n, "title": title, "text": text, "notes": notes.strip(),
                       "layout": htmlmod.unescape(label.group(1)) if label else "",
                       "words": words(title) + words(text), "notes_words": words(notes), "builds": len(steps),
                       "figures": len(re.findall(r"<(svg|img|canvas)\b", chunk, re.I)) - len(re.findall(r"<svg\b[^>]*class=[\"'][^\"']*icon", chunk, re.I)),
                       "controls": len(re.findall(r"<(input|button|select)\b", chunk, re.I))})
    layouts = collections.Counter(s["layout"] for s in slides if s["layout"])
    pictures = sum(max(0, s["figures"]) for s in slides)
    return {"slides": slides, "colours": colours, "fonts": fonts, "sizes": sizes, "layouts": layouts,
            "custom_properties": dict(list(props.items())[:80]), "remote_stylesheets": linked, "aspect": None,
            "pictures": pictures, "charts": 0, "tables": len(re.findall(r"<table\b", page, re.I))}


# ------------------------------------------------------------------------------------------------ .md (talk scripts)

def read_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^(#{1,3} .*)$", text, flags=re.M)
    slides = []
    if parts[0].strip():
        slides.append({"n": 1, "title": "", "text": parts[0].strip(), "notes": "", "layout": "", "words": words(parts[0]),
                       "notes_words": 0})
    for i in range(1, len(parts), 2):
        body = parts[i + 1] if i + 1 < len(parts) else ""
        slides.append({"n": len(slides) + 1, "title": parts[i].lstrip("#").strip(), "text": body.strip(), "notes": "",
                       "layout": "", "words": words(body), "notes_words": 0})
    return {"slides": slides, "colours": collections.Counter(), "fonts": collections.Counter(),
            "sizes": collections.Counter(), "layouts": collections.Counter(), "aspect": None, "pictures": 0, "charts": 0,
            "tables": 0, "script_words": words(text)}


# ------------------------------------------------------------------------------------------------ main

def collect(paths: list[str], kind: str) -> tuple[list[Path], list[dict]]:
    files, skipped, seen = [], [], set()
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            skipped.append({"file": str(p), "name": p.name, "skipped": "not found"})
            continue
        cands = [p] if p.is_file() or p.suffix.lower() == ".key" else sorted(
            q for q in p.rglob("*") if not any(part.startswith(".") for part in q.relative_to(p).parts)
            and "_deck" not in q.relative_to(p).parts and "node_modules" not in q.parts)
        for q in cands:
            fmt = FORMATS.get(q.suffix.lower())
            if not fmt or (q.is_dir() and fmt != "key"):
                continue
            if fmt == "md" and kind != "talk":
                continue
            rq = q.resolve()
            if rq in seen:
                continue
            seen.add(rq)
            if fmt == "key":
                skipped.append({"file": str(rq), "name": q.name, "format": "key",
                                "skipped": "Keynote files cannot be read directly: export to PDF or PPTX first "
                                           "(File > Export To), then seed the export"})
                continue
            files.append(rq)
    return files, skipped


def stem_for(path: Path, used: set) -> str:
    base = re.sub(r"[^\w-]+", "-", path.stem).strip("-")[:40] or "file"
    stem, k = base, 2
    while stem in used:
        stem, k = f"{base}-{k}", k + 1
    used.add(stem)
    return stem


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", required=True, help="the seed folder to write (created if needed)")
    ap.add_argument("--max-pages", type=int, default=12, help="page images per file, sampled evenly (default 12)")
    ap.add_argument("--kind", choices=("deck", "talk"), default="deck")
    ap.add_argument("--json", action="store_true", help="print the manifest and a summary as JSON")
    a = ap.parse_args(argv)

    out = Path(a.out).expanduser().resolve()
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for raw in a.paths:  # never write into an input
        rp = Path(raw).expanduser().resolve()
        if rp == out or rp in out.parents:
            sys.exit(f"seed_visual: --out {out} is inside an input ({rp}); choose a folder elsewhere")
    files, skipped = collect(a.paths, a.kind)
    renderer = PdfRenderer()
    tmp = Path(tempfile.mkdtemp(prefix="seed-visual-"))
    small_dir = tmp / "small"
    small_dir.mkdir()
    entries, results, used = [], [], set()
    try:
        for f in files:
            fmt = FORMATS[f.suffix.lower()]
            stem = stem_for(f, used)
            entry = {"file": str(f), "name": f.name, "sha256": sha256(f), "format": fmt, "bytes": f.stat().st_size,
                     "stem": stem, "images": []}
            try:
                if fmt == "pptx":
                    res = read_pptx(f)
                    pdf = pptx_to_pdf(f, tmp)
                    if pdf and renderer.name != "none":
                        r = renderer.run(pdf, pages_dir, small_dir, stem, a.max_pages)
                        entry["images"], entry["render"] = r["images"], f"{r['how']} (exported with LibreOffice)"
                        res["pixels"] = r["small"]
                    else:
                        entry["render"] = "none: install LibreOffice (soffice) or seed a PDF export for page images"
                elif fmt == "pdf":
                    r = renderer.run(f, pages_dir, small_dir, stem, a.max_pages)
                    texts = r["text"] or [""] * r["pages"]
                    slides = []
                    for n, t in enumerate(texts[: r["pages"]] if r["pages"] else texts, 1):
                        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
                        slides.append({"n": n, "title": clip(lines[0], 120) if lines else "", "text": "\n".join(lines[1:]),
                                       "notes": "", "layout": "", "words": words(t), "notes_words": 0})
                    res = {"slides": slides, "colours": collections.Counter(), "fonts": pdf_fonts(f),
                           "sizes": collections.Counter(), "layouts": collections.Counter(), "aspect": None,
                           "pictures": 0, "charts": 0, "tables": 0, "pixels": r["small"]}
                    entry["images"], entry["render"] = r["images"], r["how"]
                    entry["text_from"] = r["text_how"]
                    if r["how"] == "none":
                        entry["render"] = "none: no renderer (macOS swift, pdftoppm or mutool); text and fonts only"
                elif fmt == "html":
                    res = read_html(f)
                    entry["render"] = "none for HTML decks (the agent can open the deck itself)"
                else:
                    res = read_md(f)
                    entry["render"] = "none (a script)"
            except (zipfile.BadZipFile, ET.ParseError, KeyError, OSError, ValueError, subprocess.SubprocessError) as exc:
                entry["skipped"] = f"could not read: {type(exc).__name__}: {exc}"
                entries.append(entry)
                continue
            if res.get("pixels"):
                px = []
                for sp in res["pixels"]:
                    got = png_pixels(Path(sp))
                    if got:
                        px += got[2]
                if px:  # half from the pixels, half from what the file names (PPTX XML), each as shares
                    res["colours"] = blend(res["colours"], pixel_palette(px))
                res["palette_from"] = "page pixels" + (" and slide XML" if fmt == "pptx" else "")
            else:
                res["palette_from"] = {"pptx": "theme and slide XML", "html": "CSS and inline colours", "pdf": "none (no renderer)",
                                       "md": "none"}[fmt]
            res["colours"] = merge_close(res["colours"])
            entry["pages"] = len(res["slides"])
            entry["images"] = [os.path.relpath(x, out) for x in entry["images"]]
            entry["notes"] = any(s["notes"] for s in res["slides"])
            entry["summary"] = file_summary(res)
            entries.append(entry)
            results.append((entry, res))
    finally:
        renderer.close()
        shutil.rmtree(tmp, ignore_errors=True)

    manifest = {"tool": f"seed_visual {VERSION}", "created": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                "kind": a.kind, "inputs": [str(Path(x).expanduser()) for x in a.paths], "renderer": renderer.name,
                "files": entries + skipped}
    stats = overall_stats(results, a.kind)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "samples.md").write_text(samples_md(results, a.kind, manifest), encoding="utf-8")
    lines = summary_lines(results, skipped + [e for e in entries if e.get("skipped")], stats, renderer.name)
    if a.json:
        print(json.dumps({"out": str(out), "manifest": str(out / "manifest.json"), "files": manifest["files"],
                          "summary_lines": lines}, ensure_ascii=False))
    else:
        print(f"seed folder: {out}")
        for ln in lines:
            print("  " + ln)
    return 0 if results else 1


def blend(named: collections.Counter, pixels: collections.Counter) -> collections.Counter:
    """Colour weights as shares (out of 10000): all from the pixels, or half and half when the file also names colours."""
    out = collections.Counter()
    parts = [(pixels, 1.0)] if not named else [(named, 0.5), (pixels, 0.5)]
    for counter, weight in parts:
        tot = sum(counter.values()) or 1
        for h, c in counter.items():
            out[h] += round(10000 * weight * c / tot)
    return +out


def top(counter: collections.Counter, n: int) -> list:
    return [k for k, _ in counter.most_common(n)]


def file_summary(res: dict) -> dict:
    slides = res["slides"]
    tot = sum(res["colours"].values()) or 1
    s = {"slides": len(slides), "words_per_slide": summarize([x["words"] for x in slides]),
         "palette": [{"hex": h, "share": round(c / tot, 3)} for h, c in res["colours"].most_common(8)],
         "fonts": top(res["fonts"], 4), "titles": sum(1 for x in slides if x["title"]),
         "palette_from": res.get("palette_from")}
    if any(x["notes_words"] for x in slides):
        s["notes_words_per_slide"] = summarize([x["notes_words"] for x in slides])
    if res["layouts"]:
        s["layouts"] = dict(res["layouts"].most_common(6))
    if res.get("aspect"):
        s["aspect"] = res["aspect"]
    if res.get("theme"):
        s["theme"] = res["theme"]
    for k in ("pictures", "charts", "tables"):
        if res.get(k):
            s[k] = res[k]
    if any(x.get("builds") for x in slides):
        s["builds_per_slide"] = summarize([x.get("builds", 0) for x in slides])
    if res.get("custom_properties"):
        s["custom_properties"] = {k: v for k, v in res["custom_properties"].items() if parse_colour(v) or "font" in k}
    return s


def overall_stats(results: list, kind: str) -> dict:
    palette = collections.Counter()
    for _, res in results:  # each file weighs the same, whatever its length or how its colours were counted
        tot = sum(res["colours"].values())
        for h, c in res["colours"].items():
            palette[h] += c / tot if tot else 0
    palette = merge_close(palette, floor=0.0)
    n_col = sum(1 for _, r in results if r["colours"]) or 1
    fonts = collections.Counter()
    for _, res in results:
        for f, c in res["fonts"].items():
            fonts[f] += c
    sizes = collections.Counter()
    for _, res in results:
        sizes.update(res["sizes"])
    slides = [s for _, res in results for s in res["slides"]]
    layouts = collections.Counter()
    for _, res in results:
        layouts.update(res["layouts"])
    stats = {
        "kind": kind, "files": len(results), "slides": len(slides),
        "palette": [{"hex": h, "share": round(v / n_col, 4), "files": files_using(h, results), "role_hint": role_hint(h)}
                    for h, v in palette.most_common(20) if v / n_col >= 0.002],
        "fonts": [{"name": f, "count": c} for f, c in fonts.most_common(12)],
        "font_sizes": [{"size": s, "count": c} for s, c in sizes.most_common(12)],
        "words_per_slide": summarize([s["words"] for s in slides]),
        "titles": [s["title"] for s in slides if s["title"]][:200],
        "title_words": summarize([words(s["title"]) for s in slides if s["title"]]),
        "notes_words_per_slide": summarize([s["notes_words"] for s in slides if s["notes_words"]]),
        "slides_with_notes": sum(1 for s in slides if s["notes_words"]),
        "layouts": dict(layouts.most_common(15)),
        "per_file": [{"name": e["name"], "format": e["format"], **e.get("summary", {})} for e, _ in results],
    }
    builds = [s.get("builds", 0) for s in slides if "builds" in s]
    if builds:
        stats["builds_per_slide"] = summarize(builds)
    if kind == "talk":
        stats["script_words"] = sum(res.get("script_words", 0) for _, res in results)
    return stats


def files_using(hexc: str, results: list, tol: int = 6) -> int:
    rgb = tuple(int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    n = 0
    for _, res in results:
        for h in res["colours"]:
            if max(abs(a - b) for a, b in zip(rgb, (int(h[i:i + 2], 16) for i in (1, 3, 5)))) <= tol:
                n += 1
                break
    return n


def samples_md(results: list, kind: str, manifest: dict) -> str:
    out = [f"# Seed samples ({kind})", "",
           f"{len(results)} file(s) · {manifest['created']} · renderer: {manifest['renderer']}. Titles and text per slide or "
           f"page, and speaker notes where the file has them. Content is for reading the author's style; topics, results "
           f"and names never become rules.", ""]
    note_cap = 3000 if kind == "talk" else 1200
    for entry, res in results:
        s = entry["summary"]
        head = f"## {entry['name']} ({entry['format']}, {s['slides']} {'pages' if entry['format'] == 'pdf' else 'slides'}"
        head += f", {s['aspect']})" if s.get("aspect") else ")"
        out += [head, ""]
        meta = []
        if s.get("palette"):
            meta.append("palette: " + ", ".join(f"{p['hex']} {p['share']:.0%}" for p in s["palette"][:6]))
        if s.get("fonts"):
            meta.append("fonts: " + ", ".join(s["fonts"]))
        if s.get("words_per_slide"):
            meta.append(f"words per slide: median {s['words_per_slide']['median']}, max {s['words_per_slide']['max']}")
        if entry.get("images"):
            meta.append(f"page images: {', '.join(entry['images'][:4])}" + (" …" if len(entry["images"]) > 4 else ""))
        out += [f"- {m}" for m in meta] + [""]
        for sl in res["slides"][:60]:
            out.append(f"### {sl['n']}" + (f" · {sl['layout']}" if sl.get("layout") else "")
                       + (f" · {sl['title']}" if sl.get("title") else ""))
            if sl["text"]:
                out += ["", clip(sl["text"], 900)]
            if sl["notes"]:
                out += ["", "Notes: " + clip(sl["notes"], note_cap)]
            out.append("")
        if len(res["slides"]) > 60:
            out += [f"(… {len(res['slides']) - 60} more)", ""]
    return "\n".join(out) + "\n"


def summary_lines(results: list, skipped: list, stats: dict, renderer: str) -> list[str]:
    lines = []
    for e, res in results:
        s = e["summary"]
        wps = s.get("words_per_slide", {})
        lines.append(f"{e['name']}: {e['format']}, {s['slides']} slides or pages, words per slide median "
                     f"{wps.get('median', 0)}, {len(e.get('images', []))} page image(s); fonts "
                     f"{', '.join(s.get('fonts', [])[:3]) or 'none found'}")
    if stats["palette"]:
        lines.append("palette (share over files): " + ", ".join(f"{p['hex']} {p['share']:.0%}" for p in stats["palette"][:8]))
    if any(not e.get("images") for e, _ in results if e["format"] in ("pdf", "pptx")):
        lines.append(f"page images: renderer {renderer}; PPTX needs LibreOffice for images (or seed a PDF export)")
    for s in skipped:
        lines.append(f"skipped {s.get('name')}: {s.get('skipped')}")
    return lines


if __name__ == "__main__":
    sys.exit(main())
