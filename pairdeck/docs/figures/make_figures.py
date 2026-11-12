#!/usr/bin/env python3
"""Draw the README figures: each as NAME.svg (light) and NAME-dark.svg (dark), for GitHub's <picture> switch.

Run: python3 docs/figures/make_figures.py
Same helpers and colour roles as PairTeX's figures: blue is the author, purple the agent, green the replies, gold the style
guide. Figures use system fonts (CMU Serif if installed, else Georgia), so every line is broken by hand and kept short.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

LIGHT = dict(ink="#232323", ink2="#6B6B6B", line="#BDBDBD", rule="#D9D9D9", wash="#F6F6F4", bar="#F1F1EE",
             skel="#E4E4E1", paper="#FFFFFF", dot="#D9D9D9", grey="#9A9A9A",
             you="#27709C", you_soft="#EAF2F8", tool="#6D5398", tool_soft="#F3EEF8", note="#227828", note_soft="#EDF5EC",
             gold="#C6952C", gold_ink="#8A6410", gold_soft="#FBF6E9", gold_line="#E5D3A6", on_gold="#FFFFFF",
             bad="#B4463C", bad_soft="#FBEDEB", teal="#3F8A7E", orange="#C07338", orange_soft="#F5E6DB")
DARK = dict(ink="#E6EDF3", ink2="#9198A1", line="#3D444D", rule="#30363D", wash="#161B22", bar="#21262D",
            skel="#30363D", paper="#161B22", dot="#484F58", grey="#7D8590",
            you="#5AA8DA", you_soft="#0F2536", tool="#B39DDB", tool_soft="#231C33", note="#5DBB63", note_soft="#12261A",
            gold="#D4A33A", gold_ink="#E3B95A", gold_soft="#261E0F", gold_line="#5A4520", on_gold="#0D1117",
            bad="#E5786D", bad_soft="#2D1614", teal="#7FC8BA", orange="#E39A62", orange_soft="#33261D")

SERIF = "'CMU Serif','Latin Modern Roman',Georgia,'Times New Roman',serif"
MONO = "Menlo,'SF Mono',Consolas,'DejaVu Sans Mono',monospace"


def svg(w: int, h: int, label: str, body: str, c: dict) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{label}">\n<style>text{{font-family:{SERIF};fill:{c["ink"]}}} .m{{font-family:{MONO}}} '
            f'.b{{font-weight:700}} .i{{font-style:italic}}</style>\n'
            f'<defs>{"".join(marker(n, c[k]) for n, k in (("a", "ink2"), ("ag", "gold"), ("ap", "tool"), ("ay", "you"), ("an", "note")))}'
            f'</defs>\n{body}\n</svg>\n')


def marker(name: str, color: str) -> str:
    return (f'<marker id="{name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9 Z" fill="{color}"/></marker>')


def badge(x: float, y: float, n: str, c: dict, r: float = 11) -> str:
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c["gold"]}"/>'
            f'<text x="{x}" y="{y + 5.2}" font-size="15" class="b" text-anchor="middle" fill="{c["on_gold"]}" '
            f'style="fill:{c["on_gold"]}">{n}</text>')


def t(x, y, s, size=15.5, fill=None, cls="", anchor="start", extra=""):
    f = f' style="fill:{fill}"' if fill else ""
    k = f' class="{cls}"' if cls else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x}" y="{y}" font-size="{size}"{k}{a}{f}{extra}>{s}</text>'


def window(x, y, w, h, name, c) -> str:
    """A browser window with a title bar: the review page."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
            f'<path d="M{x},{y + 8} a8,8 0 0 1 8,-8 h{w - 16} a8,8 0 0 1 8,8 v22 h-{w} Z" fill="{c["bar"]}"/>'
            f'<circle cx="{x + 17}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/><circle cx="{x + 32}" cy="{y + 15}" r="4.5" '
            f'fill="{c["dot"]}"/><circle cx="{x + 47}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/>'
            f'<rect x="{x + 62}" y="{y + 6}" width="{w - 74}" height="18" rx="9" fill="{c["paper"]}"/>'
            + t(x + 74, y + 20, name, 13, c["ink2"], "m"))


def bars(x, y, c, w1=118, w2=104, h=16, gap=10, labels=False):
    """Two growing bars of a mini slide: option A (blue) and B (teal)."""
    out = [f'<path d="M{x},{y - 6} V{y + 2 * h + gap + 6}" stroke="{c["line"]}" stroke-width="1.4"/>',
           f'<rect x="{x}" y="{y}" width="{w1}" height="{h}" rx="2" fill="{c["you"]}" opacity=".85"/>',
           f'<rect x="{x}" y="{y + h + gap}" width="{w2}" height="{h}" rx="2" fill="{c["teal"]}" opacity=".85"/>']
    if labels:
        out += [t(x + w1 + 6, y + 13, "93%", 14, c["you"]), t(x + w2 + 6, y + h + gap + 13, "87%", 14, c["teal"])]
    return "".join(out)


ICONS = {
    "deck": '<rect x="10" y="12" width="30" height="22" rx="3"/><path d="M6 8h30M16 40h18M25 34v6M16 27v-6M24 27v-9M32 27v-4"/>',
    "people": '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="16" r="6"/>'
              '<path d="M6 40c0-7 5-12 11-12s11 5 11 12M24 31c2-2 5-3 9-3 6 0 11 5 11 12"/>',
    "eye": '<path d="M4 24c5-9 12-14 20-14s15 5 20 14c-5 9-12 14-20 14S9 33 4 24z"/><circle cx="24" cy="24" r="6"/>',
    "box": '<path d="M24 5l17 9v20L24 43 7 34V14z"/><path d="M7 14l17 9 17-9M24 23v20"/>',
}


# ------------------------------------------------------------------------------------------------------------- banner

def banner(c: dict) -> str:
    body = [
        t(4, 26, "OPEN SOURCE  ·  MIT LICENSE  ·  FOR EXPLAINER AND REPORT DECKS", 13.5, c["ink2"], extra=' letter-spacing="2.2"'),
        '<text x="0" y="104" font-size="78" class="b" letter-spacing="-1">PairDeck</text>',
        # three stacked slides, the front one with two bars that build up
        f'<rect x="462" y="36" width="78" height="52" rx="5" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>',
        f'<rect x="452" y="46" width="78" height="52" rx="5" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>',
        f'<rect x="442" y="56" width="78" height="52" rx="5" fill="{c["paper"]}" stroke="{c["ink2"]}" stroke-width="1.8"/>',
        f'<rect x="454" y="70" width="44" height="9" rx="2" fill="{c["you"]}"/>',
        f'<rect x="454" y="85" width="34" height="9" rx="2" fill="{c["teal"]}"/>',
        f'<rect x="488" y="66" width="26" height="31" rx="3" fill="none" stroke="{c["you"]}" stroke-width="1.6" stroke-dasharray="4 3"/>',
        f'<text x="2" y="150" font-size="25">Animated explainer decks with your '
        f'<tspan class="b" style="fill:{c["tool"]}">AI agent</tspan>, in a style that learns yours.</text>',
        f'<rect x="2" y="168" width="170" height="3" fill="{c["gold"]}"/>',
    ]
    return svg(960, 180, "PairDeck: animated explainer decks with your AI agent, in a style that learns yours",
               "\n".join(body), c)


# --------------------------------------------------------------------------------------------------------------- loop

def loop(c: dict) -> str:
    b = []
    b += [badge(22, 14, "1", c), t(40, 20, "You comment on a slide", 17, c["you"], "b"),
          badge(352, 14, "2", c), t(370, 20, "The agent answers", 17, c["tool"], "b"),
          badge(668, 14, "3", c), t(686, 20, "The deck updates", 17, None, "b")]
    # 1. the review page with a box and a comment
    b.append(window(10, 34, 292, 250, "review page", c))
    b.append(f'<rect x="28" y="78" width="150" height="8" rx="4" fill="{c["skel"]}"/>')
    b.append(bars(50, 104, c))
    b.append(f'<rect x="40" y="94" width="186" height="64" rx="5" fill="{c["you_soft"]}" fill-opacity=".55" '
             f'stroke="{c["you"]}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    b.append(f'<rect x="28" y="178" width="256" height="92" rx="7" fill="{c["paper"]}" stroke="{c["you"]}" stroke-width="1.6"/>')
    b.append(t(40, 200, '<tspan class="b">Ada:</tspan> label each bar;', 15, c["you"]))
    b.append(t(40, 220, "drop the legend, it makes", 15, c["you"]))
    b.append(t(40, 240, "me look back and forth", 15, c["you"]))
    b.append(f'<rect x="222" y="244" width="50" height="20" rx="10" fill="{c["you"]}"/>' +
             t(247, 258, "Send", 13, c["paper"], "b", "middle"))
    b.append(f'<path d="M306,159 L334,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 2. the agent
    b.append(f'<rect x="340" y="70" width="290" height="178" rx="8" fill="{c["tool_soft"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(t(485, 99, "Your agent + pairdeck", 17.5, c["tool"], "b", "middle"))
    b.append(t(485, 119, "(Claude Code, Codex, …)", 14.5, c["ink2"], anchor="middle"))
    for n, s in enumerate(["picks up the comment and box", "reads the slide and your style",
                           "edits the deck, screenshots it", "replies under your comment"]):
        b.append(f'<circle cx="358" cy="{146 + 25 * n}" r="3.5" fill="{c["tool"]}"/>' + t(370, 151 + 25 * n, s, 15))
    b.append(f'<path d="M634,159 L660,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 3. the review page again: labelled bars and a reply
    b.append(window(664, 34, 288, 250, "review page", c))
    b.append(f'<rect x="682" y="78" width="150" height="8" rx="4" fill="{c["skel"]}"/>')
    b.append(t(696, 117, "A", 15, c["you"], anchor="end") + t(696, 143, "B", 15, c["teal"], anchor="end"))
    b.append(bars(704, 104, c, labels=True))
    b.append(f'<rect x="680" y="178" width="256" height="92" rx="7" fill="{c["note_soft"]}"/>'
             f'<rect x="680" y="178" width="3" height="92" fill="{c["note"]}"/>')
    b.append(t(692, 200, '<tspan class="b">Claude:</tspan> labelled each', 15, c["note"]))
    b.append(t(692, 220, "bar at its end; legend gone,", 15, c["note"]))
    b.append(t(692, 240, "on slides 3, 4 and 7.", 15, c["note"]))
    b.append(f'<rect x="868" y="244" width="56" height="20" rx="10" fill="none" stroke="{c["note"]}" stroke-width="1.4"/>' +
             t(896, 258, "Keep", 13, c["note"], "b", "middle"))
    # 4. the style guide
    b.append(f'<rect x="340" y="318" width="290" height="64" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(badge(360, 337, "4", c))
    b.append(t(378, 343, "Your style guide", 17.5, c["gold_ink"], "b"))
    b.append(t(360, 368, "STYLE.md: plain text, in git", 14.5))
    b.append(f'<path d="M808,288 C808,340 724,350 634,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M156,288 C156,340 240,350 336,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M485,316 L485,252" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#ap)"/>')
    b.append(t(476, 290, "read before every deck", 14.5, c["tool"], anchor="end"))
    b.append(t(950, 381, "what you keep, rewrite or undo", 14.5, c["gold_ink"], anchor="end"))
    b.append(t(12, 381, "and the decks you made before", 14.5, c["gold_ink"]))
    b.append(t(950, 406, "Accept: Keep. Not quite: Follow up, or edit the slide yourself.", 14.5, c["ink2"], anchor="end"))
    return svg(960, 414, "The PairDeck loop: you drag a box on a slide and comment, the agent edits the deck and replies under "
               "your comment, and what you keep, rewrite or undo teaches your style guide", "\n".join(b), c)


# ------------------------------------------------------------------------------------------------------------ before/after

def versus(c: dict) -> str:
    b = []
    b.append(f'<rect x="0" y="0" width="470" height="300" rx="8" fill="{c["wash"]}"/>'
             f'<rect x="0" y="0" width="470" height="4" fill="{c["grey"]}"/>')
    b.append(t(20, 36, "Slides with a chatbot", 18, c["ink2"], "b"))
    # a slide app and a chat window
    b.append(f'<rect x="20" y="62" width="160" height="108" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>')
    b.append(f'<rect x="34" y="78" width="96" height="7" rx="3" fill="{c["skel"]}"/>')
    b.append(bars(44, 100, c, 92, 70, 14, 9))
    b.append(f'<rect x="306" y="62" width="140" height="108" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
             f'<rect x="318" y="78" width="90" height="20" rx="10" fill="{c["skel"]}"/>'
             f'<rect x="344" y="106" width="90" height="20" rx="10" fill="{c["skel"]}"/>'
             f'<rect x="318" y="134" width="74" height="20" rx="10" fill="{c["skel"]}"/>')
    b.append(f'<path d="M186,94 C222,70 266,70 300,94" stroke="{c["grey"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(f'<path d="M300,138 C266,162 222,162 186,138" stroke="{c["grey"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(t(243, 62, "“the second bar, top right…”", 13.5, c["ink2"], anchor="middle"))
    b.append(t(243, 186, "re-export, fix the layout", 13.5, c["ink2"], anchor="middle"))
    b.append(t(243, 121, "× every round", 14, c["bad"], "b", "middle"))
    for n, s in enumerate(["You say where on the slide, in words.", "Every deck starts from a stock template.",
                           "It forgets the corrections you made."]):
        y = 226 + 26 * n
        b.append(f'<circle cx="31" cy="{y - 5}" r="9" fill="{c["bad_soft"]}"/>'
                 f'<path d="M27,{y - 9} l8,8 M35,{y - 9} l-8,8" stroke="{c["bad"]}" stroke-width="2" stroke-linecap="round"/>')
        b.append(t(48, y, s, 15.5))
    # right: PairDeck
    b.append(f'<rect x="490" y="0" width="470" height="300" rx="8" fill="{c["tool_soft"]}"/>'
             f'<rect x="490" y="0" width="470" height="4" fill="{c["tool"]}"/>')
    b.append(t(510, 36, "With PairDeck", 18, c["tool"], "b"))
    b.append(window(514, 56, 250, 124, "review page", c))
    b.append(f'<rect x="530" y="98" width="110" height="7" rx="3" fill="{c["skel"]}"/>')
    b.append(bars(546, 118, c, 100, 84, 13, 8))
    b.append(f'<rect x="538" y="110" width="128" height="50" rx="4" fill="none" stroke="{c["you"]}" stroke-width="1.6" '
             f'stroke-dasharray="5 4"/>')
    b.append(f'<rect x="676" y="104" width="78" height="34" rx="6" fill="{c["paper"]}" stroke="{c["you"]}" stroke-width="1.4"/>'
             + t(684, 125, "label these", 13, c["you"]))
    b.append(f'<rect x="676" y="142" width="78" height="26" rx="6" fill="{c["note_soft"]}"/>' + t(684, 159, "done ✓", 13, c["note"]))
    b.append(f'<circle cx="884" cy="116" r="34" fill="{c["paper"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(f'<path d="M870,106 h28 v20 h-28 z M876,100 v6 M892,100 v6 M877,115 h3 M888,115 h3 M878,121 h12" stroke="{c["tool"]}" '
             f'stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(t(884, 168, "the agent, in", 13.5, c["tool"], anchor="middle"))
    b.append(t(884, 184, "the background", 13.5, c["tool"], anchor="middle"))
    b.append(f'<path d="M770,100 C800,90 822,94 846,104" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="5 4" fill="none" marker-end="url(#ap)"/>')
    b.append(f'<path d="M846,130 C822,142 800,146 770,138" stroke="{c["note"]}" stroke-width="2" fill="none" marker-end="url(#an)"/>')
    for n, s in enumerate(["Point at the slide: drag a box, type, send.", "The agent edits and checks every slide.",
                           "It learns your palette, type and density."]):
        y = 226 + 26 * n
        b.append(f'<circle cx="521" cy="{y - 5}" r="9" fill="{c["note_soft"]}"/>'
                 f'<path d="M516,{y - 5} l4,4 l7,-8" stroke="{c["note"]}" stroke-width="2" fill="none" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
        b.append(t(538, y, s, 15.5))
    return svg(960, 300, "With a chatbot you describe the spot on the slide in words every round and it forgets your "
               "corrections; with PairDeck you drag a box on the slide, the agent edits in the background, and it learns "
               "your style", "\n".join(b), c)


# --------------------------------------------------------------------------------------------------------------- style

def style(c: dict) -> str:
    b = [t(10, 18, "What you do", 15.5, c["ink2"])]
    acts = [("You rewrite", "part of a slide", "strongest"), ("You undo", "a change", "never again"),
            ("You state", "a preference", "“always …”"), ("You add", "your own slide", "style, not content"),
            ("You press", "Keep", "confirms a rule")]
    for n, (v, rest, tag) in enumerate(acts):
        y = 30 + 54 * n
        b.append(f'<rect x="10" y="{y}" width="340" height="46" rx="6" fill="{c["you_soft"]}" stroke="{c["you"]}" stroke-width="1.6"/>')
        b.append(t(24, y + 29, f'<tspan class="b">{v}</tspan> {rest}', 16))
        b.append(t(338, y + 29, tag, 14.5, c["you"], "i", "end"))
        b.append(f'<path d="M352,{y + 23} C380,{y + 23} 380,161 404,161" stroke="{c["grey"]}" stroke-width="1.6" fill="none"/>')
    b.append(f'<path d="M404,161 L414,161" stroke="{c["grey"]}" stroke-width="1.6" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="418" y="118" width="160" height="86" rx="6" fill="{c["wash"]}" stroke="{c["grey"]}" stroke-width="1.6"/>')
    b.append(t(498, 148, "Evidence log", 16, None, "b", "middle"))
    b.append(t(498, 170, "each event with", 14.5, c["ink2"], anchor="middle"))
    b.append(t(498, 189, "its slide and diff", 14.5, c["ink2"], anchor="middle"))
    b.append(f'<path d="M580,161 L606,161" stroke="{c["grey"]}" stroke-width="1.6" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="612" y="12" width="346" height="282" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(t(630, 40, "STYLE.md", 17, c["gold_ink"], "b"))
    b.append(t(940, 40, "yours to edit", 14.5, c["gold_ink"], anchor="end"))
    b.append(f'<line x1="630" y1="50" x2="940" y2="50" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    rows = [(76, "Base rules", "only you add these"), (108, "Confirmed rules", "3 pieces of evidence"),
            (196, "Tentative patterns", "seen once or twice"), (226, "Palette, type and layout", ""),
            (256, "What you undid", "never repeated")]
    for y, k, v in rows:
        b.append(t(630, y, k, 15.5, None, "b"))
        if v:
            b.append(t(940, y, v, 14.5, c["ink2"], anchor="end"))
    for n, col in enumerate(["you", "teal", "orange"]):
        b.append(f'<rect x="{866 + 24 * n}" y="214" width="16" height="16" rx="3" fill="{c[col]}"/>')
    b.append(f'<rect x="630" y="118" width="310" height="52" rx="4" fill="{c["paper"]}" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    b.append(t(640, 139, "e.g. Label bars at their ends;", 14.5, cls="i"))
    b.append(t(640, 159, "no legends, no more than one chart.", 14.5, cls="i"))
    b.append(t(630, 282, "Every change is a git commit you can undo.", 14.5, c["ink2"]))
    b.append(f'<path d="M784,298 C784,318 704,322 622,322" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" '
             f'fill="none" marker-end="url(#ap)"/>')
    b.append(t(614, 327, "the agent reads it before every deck", 15, c["tool"], anchor="end"))
    return svg(960, 336, "How the style guide learns: your rewrites, undos, stated preferences, own slides and Keep clicks "
               "become evidence, distilled into STYLE.md, which the agent reads before every deck", "\n".join(b), c)


# ---------------------------------------------------------------------------------------------------------------- seed

def seed(c: dict) -> str:
    b = [t(10, 18, "Decks you already made", 15.5, c["ink2"])]
    files = [(".pptx", "a course lecture"), (".pdf", "a conference talk"), (".html", "an old explainer"),
             (".key", "export to PDF first")]
    for n, (ext, what) in enumerate(files):
        y = 32 + 50 * n
        faint = ext == ".key"
        dash = ' stroke-dasharray="5 4"' if faint else ""
        b.append(f'<rect x="10" y="{y}" width="250" height="40" rx="6" fill="{c["paper"]}" stroke="{c["line"]}" '
                 f'stroke-width="1.4"{dash}/>')
        b.append(t(24, y + 26, ext, 15, c["ink2"] if faint else c["you"], "m b"))
        b.append(t(92, y + 26, what, 15, c["ink2"] if faint else None, "i" if faint else ""))
    b.append(f'<path d="M266,120 L296,120" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="302" y="22" width="300" height="206" rx="8" fill="{c["tool_soft"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(t(452, 50, "pairdeck seed", 17, c["tool"], "m b", "middle"))
    for n, s in enumerate(["palette, with how much each is used", "fonts and sizes", "words per slide, titles, notes",
                           "page images to look at"]):
        b.append(f'<circle cx="322" cy="{80 + 26 * n}" r="3.5" fill="{c["tool"]}"/>' + t(334, 85 + 26 * n, s, 15))
    b.append(t(452, 208, "on your computer; files untouched", 14, c["ink2"], "i", "middle"))
    b.append(f'<path d="M608,120 L638,120" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="644" y="22" width="314" height="206" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(t(660, 50, "STYLE.md, drafted", 17, c["gold_ink"], "b"))
    rows = [("S01", "Titles state a claim", "5 of 5"), ("S02", "Navy for the method", "4 of 5"),
            ("T01", "One chart a slide", "2 of 5"), ("T02", "Under 30 words a slide", "2 of 5")]
    for n, (rid, rule, ev) in enumerate(rows):
        y = 84 + 30 * n
        b.append(t(660, y, rid, 14, c["gold_ink"], "m b") + t(700, y, rule, 15) + t(944, y, ev, 14, c["ink2"], anchor="end"))
    b.append(t(660, 208, "content never becomes a rule", 14, c["ink2"], "i"))
    b.append(f'<path d="M800,232 C800,256 700,262 612,262" stroke="{c["you"]}" stroke-width="2" fill="none" marker-end="url(#ay)"/>')
    b.append(t(604, 267, "you keep, edit or delete each one", 15, c["you"], anchor="end"))
    return svg(960, 280, "Seeding: pairdeck seed reads your past .pptx, .pdf and .html decks on your computer (palette, "
               "fonts, words per slide, titles, page images); the agent drafts STYLE.md entries with how many decks support "
               "each; you keep, edit or delete them", "\n".join(b), c)


FIGURES = {"banner": banner, "loop": loop, "versus": versus, "style": style, "seed": seed}

if __name__ == "__main__":
    for name, fn in FIGURES.items():
        (HERE / f"{name}.svg").write_text(fn(LIGHT), encoding="utf-8")
        (HERE / f"{name}-dark.svg").write_text(fn(DARK), encoding="utf-8")
        print(f"wrote {name}.svg, {name}-dark.svg")
