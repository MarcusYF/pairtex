#!/usr/bin/env python3
"""figdata: recover the plotted data from a matplotlib figure saved as a vector PDF, so a poster can redraw it in its own style.

A matplotlib PDF keeps every plotted point as an exact coordinate in its drawing operations. This reads them back: each line
(a stroked path with three or more points), each filled band that shares a line's colour (`fill_between`, e.g. error bands),
and the axis mapping from the tick labels and the grid or tick marks next to them. Linear axes, one plot per file.

    python3 figdata.py figure.pdf > figure.json

Output: {"x_ticks": [[pdf_x, value], ...], "y_ticks": [...], "series": [{"color", "x", "y", "lo", "hi"}, ...]} in data units,
in drawing order (matplotlib draws series in legend order). Standard library only. Check the result against the figure: a
log axis, several subplots or markers without lines need more than this.
"""
import json
import re
import sys
import zlib

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def content_stream(path: str) -> str:
    """The page's drawing operations: the decompressed stream with the most path operators."""
    data = open(path, "rb").read()
    best, score = "", -1
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        raw = m.group(1)
        try:
            text = zlib.decompress(raw).decode("latin-1")
        except zlib.error:
            text = raw.decode("latin-1", "replace")
        s = text.count(" l\n") + text.count(" Td")
        if s > score:
            best, score = text, s
    return best


def parse(text: str):
    toks = re.findall(r"\((?:\\.|[^\\)])*\)|\[[^\]]*\]|/[^\s/\[\]()<>]+|" + NUM + r"|[A-Za-z*'\"]+", text)
    stack, path, paths, texts = [], [], [], []
    stroke = fill = None
    td = None
    size = 10.0
    moved = [False]  # per q/Q level: is a transform (cm) in force? Legend and axis labels are drawn translated.
    for t in toks:
        if re.fullmatch(NUM, t):
            stack.append(float(t))
            continue
        if t[0] in "(/[":
            stack.append(t)
            continue
        op = t
        nums = [x for x in stack if isinstance(x, float)]
        if op == "RG" and len(nums) >= 3:
            stroke = tuple(round(x, 4) for x in nums[-3:])
        elif op == "rg" and len(nums) >= 3:
            fill = tuple(round(x, 4) for x in nums[-3:])
        elif op == "G" and nums:
            stroke = (round(nums[-1], 4),) * 3
        elif op == "g" and nums:
            fill = (round(nums[-1], 4),) * 3
        elif op == "m" and len(nums) >= 2:
            path.append([(nums[-2], nums[-1])])
        elif op == "l" and len(nums) >= 2 and path:
            path[-1].append((nums[-2], nums[-1]))
        elif op in ("S", "s", "B", "B*", "b", "b*", "f", "f*", "F"):
            for sub in path:
                paths.append({"op": op, "stroke": stroke, "fill": fill, "pts": sub, "moved": moved[-1]})
            path = []
        elif op == "n":
            path = []
        elif op == "q":
            moved.append(moved[-1])
        elif op == "Q" and len(moved) > 1:
            moved.pop()
        elif op == "cm" and len(nums) >= 6:
            moved[-1] = True
        elif op == "Tf" and nums:
            size = nums[-1]
        elif op == "Td" and len(nums) >= 2:
            td = (nums[-2], nums[-1])
        elif op == "Tj" and td is not None and not moved[-1] and stack and isinstance(stack[-1], str) and stack[-1].startswith("("):
            label = stack[-1][1:-1].replace("\\-", "-")
            # Td is the baseline's left end; digits are about 0.6 em wide and 0.73 em tall. Keep the centre and the right end:
            # x labels are centred under their ticks, y labels right-aligned beside theirs.
            w = 0.6 * size * len(label)
            texts.append((label, (td[0] + w / 2, td[1] + 0.36 * size, td[0] + w)))
        if op != "Tf":
            stack = []
    return paths, texts


def straight(p, horizontal: bool) -> bool:
    (x0, y0), (x1, y1) = p["pts"][0], p["pts"][-1]
    return len(p["pts"]) == 2 and (abs(y0 - y1) < 1e-6 if horizontal else abs(x0 - x1) < 1e-6)


def fit(pairs):
    n = len(pairs)
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    den = sum((a - mx) ** 2 for a, _ in pairs)
    k = sum((a - mx) * (b - my) for a, b in pairs) / den
    return k, my - k * mx


def axes(paths, texts):
    """Pair numeric tick labels with the vertical (x) and horizontal (y) grid lines or tick marks nearest to them."""
    vlines = sorted({round(p["pts"][0][0], 3) for p in paths if p["op"] in ("S", "B") and straight(p, False)})
    hlines = sorted({round(p["pts"][0][1], 3) for p in paths if p["op"] in ("S", "B") and straight(p, True)})
    labels = [(float(s.replace("−", "-")), xy) for s, xy in texts if re.fullmatch(r"[-−]?\d+(\.\d+)?", s)]
    if not labels:
        raise SystemExit("figdata: no numeric tick labels found (text drawn as paths? a log axis?)")
    # x tick labels: the largest row of numeric labels at one height; y tick labels: the largest column at one x
    rows, cols = {}, {}
    for v, (x, y, right) in labels:
        rows.setdefault(round(y, 1), []).append((v, x, y))
        cols.setdefault(round(right / 2) * 2, []).append((v, x, y))  # right-aligned: group by the right end
    xrow = max(rows.values(), key=len)
    ycol = max(cols.values(), key=len)
    xs = [(min(vlines, key=lambda q: abs(q - x)), v) for v, x, _ in xrow] if vlines else []
    ys = [(min(hlines, key=lambda q: abs(q - y)), v) for v, _, y in ycol] if hlines else []
    xs = sorted(set(xs))
    ys = sorted(set(ys))
    if len(xs) < 2 or len(ys) < 2:
        raise SystemExit("figdata: could not pair at least two ticks per axis")
    return xs, ys


def main(path: str) -> dict:
    paths, texts = parse(content_stream(path))
    xs, ys = axes(paths, texts)
    kx, bx = fit(xs)
    ky, by = fit(ys)
    X = lambda x: kx * x + bx  # noqa: E731
    Y = lambda y: ky * y + by  # noqa: E731
    lines = [p for p in paths if p["op"] == "S" and not p["moved"] and len(p["pts"]) >= 3
             and len({round(x, 3) for x, _ in p["pts"]}) >= 3]
    if lines:  # legend samples are short lines: keep the ones spanning a good part of the data's width
        span = lambda p: max(x for x, _ in p["pts"]) - min(x for x, _ in p["pts"])  # noqa: E731
        widest = max(span(p) for p in lines)
        lines = [p for p in lines if span(p) >= 0.25 * widest]
    bands = [p for p in paths if p["op"] in ("B", "f", "f*") and not p["moved"] and len(p["pts"]) >= 6
             and p["fill"] not in (None, (1.0, 1.0, 1.0))]
    out = {"source": path, "x_ticks": xs, "y_ticks": ys, "series": []}
    for ln in lines:
        n = len(ln["pts"])
        band = next((b for b in bands if b["fill"] == ln["stroke"] and len(b["pts"]) >= 2 * n), None)
        lo = hi = None
        if band:  # fill_between: start point, n lower points, n upper points back, closing point
            pts = band["pts"]
            lower, upper = pts[1:1 + n], pts[1 + n:1 + 2 * n][::-1]
            if len(lower) == n and len(upper) == n:
                lo = [round(Y(y), 6) for _, y in lower]
                hi = [round(Y(y), 6) for _, y in upper]
        col = ln["stroke"] or (0, 0, 0)
        out["series"].append({"color": "#%02x%02x%02x" % tuple(round(c * 255) for c in col),
                              "x": [round(X(x), 6) for x, _ in ln["pts"]], "y": [round(Y(y), 6) for _, y in ln["pts"]],
                              "lo": lo, "hi": hi})
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(json.dumps(main(sys.argv[1]), indent=1))
