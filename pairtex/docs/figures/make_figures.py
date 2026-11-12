#!/usr/bin/env python3
"""Draw the README figures: each as NAME.svg (light) and NAME-dark.svg (dark), for GitHub's <picture> switch.

Run: python3 docs/figures/make_figures.py
Colours follow the pitch: blue is the author, purple the agent, green the notes as they print, gold the style guide.
Figures use system fonts (CMU Serif if installed, else Georgia), so every line is broken by hand and kept short.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

LIGHT = dict(ink="#232323", ink2="#6B6B6B", line="#BDBDBD", rule="#D9D9D9", wash="#F6F6F4", bar="#F1F1EE",
             skel="#E4E4E1", paper="#FFFFFF", dot="#D9D9D9", grey="#9A9A9A",
             you="#27709C", you_soft="#EAF2F8", tool="#6D5398", tool_soft="#F3EEF8", note="#227828", note_soft="#EDF5EC",
             gold="#C6952C", gold_ink="#8A6410", gold_soft="#FBF6E9", gold_line="#E5D3A6", on_gold="#FFFFFF",
             bad="#B4463C", bad_soft="#FBEDEB")
DARK = dict(ink="#E6EDF3", ink2="#9198A1", line="#3D444D", rule="#30363D", wash="#161B22", bar="#21262D",
            skel="#30363D", paper="#161B22", dot="#484F58", grey="#7D8590",
            you="#5AA8DA", you_soft="#0F2536", tool="#B39DDB", tool_soft="#231C33", note="#5DBB63", note_soft="#12261A",
            gold="#D4A33A", gold_ink="#E3B95A", gold_soft="#261E0F", gold_line="#5A4520", on_gold="#0D1117",
            bad="#E5786D", bad_soft="#2D1614")

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


def editor(x, y, w, h, name, c) -> str:
    """A window with a title bar: the author's editor."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
            f'<path d="M{x},{y + 8} a8,8 0 0 1 8,-8 h{w - 16} a8,8 0 0 1 8,8 v22 h-{w} Z" fill="{c["bar"]}"/>'
            f'<circle cx="{x + 17}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/><circle cx="{x + 32}" cy="{y + 15}" r="4.5" '
            f'fill="{c["dot"]}"/><circle cx="{x + 47}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/>'
            + t(x + 66, y + 20, name, 14, c["ink2"], "m"))


# ------------------------------------------------------------------------------------------------------------- banner

def banner(c: dict) -> str:
    body = [
        t(4, 26, "OPEN SOURCE  ·  MIT LICENSE  ·  FOR LATEX PAPERS", 13.5, c["ink2"], extra=' letter-spacing="2.2"'),
        # PairTeX, with the E lowered as in the TeX logo
        f'<text x="0" y="104" font-size="78" class="b" letter-spacing="-1">Pair<tspan>T</tspan>'
        f'<tspan dx="-9" dy="15">E</tspan><tspan dx="-8" dy="-15">X</tspan></text>',
        f'<text x="2" y="150" font-size="25">Pair-write your LaTeX paper with an '
        f'<tspan class="b" style="fill:{c["tool"]}">AI coauthor</tspan>, without leaving your editor.</text>',
        f'<rect x="2" y="168" width="170" height="3" fill="{c["gold"]}"/>',
    ]
    return svg(960, 180, "PairTeX: pair-write your LaTeX paper with an AI coauthor, without leaving your editor",
               "\n".join(body), c)


# --------------------------------------------------------------------------------------------------------------- loop

def loop(c: dict) -> str:
    b = []
    b += [badge(22, 14, "1", c), t(40, 20, "You comment in your editor", 17, c["you"], "b"),
          badge(352, 14, "2", c), t(370, 20, "The agent answers", 17, c["tool"], "b"),
          badge(662, 14, "3", c), t(680, 20, "Both land in the paper", 17, None, "b")]
    # 1. the editor
    b.append(editor(10, 34, 292, 250, "main.tex", c))
    b.append(f'<rect x="20" y="140" width="196" height="22" rx="3" fill="{c["you_soft"]}"/>')
    lines = ["Iterative preference", "optimization trains a", "policy on its samples,"]
    b += [t(24, 90 + 22 * n, s, 14.5, cls="m") for n, s in enumerate(lines)]
    b.append(f'<text x="24" y="156" font-size="14.5" class="m"><tspan class="b" style="fill:{c["you"]}">[[</tspan>'
             f'reference refresh<tspan class="b" style="fill:{c["you"]}">]]</tspan> at</text>')
    b.append(t(24, 178, "every round.", 14.5, cls="m"))
    b.append(f'<text x="24" y="210" font-size="14.5" class="m" style="fill:{c["you"]}"><tspan class="b">%!</tspan> too much jargon;</text>')
    b.append(t(24, 232, "%  define it before", 14.5, c["you"], "m"))
    b.append(f'<text x="24" y="254" font-size="14.5" class="m" style="fill:{c["you"]}">%  using it, max 5 lines'
             f'<tspan class="b">..</tspan></text>')
    b.append(f'<path d="M306,159 L334,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 2. the agent
    b.append(f'<rect x="340" y="70" width="282" height="178" rx="8" fill="{c["tool_soft"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(t(481, 99, "Your agent + pairtex", 17.5, c["tool"], "b", "middle"))
    b.append(t(481, 119, "(Claude Code, Codex, …)", 14.5, c["ink2"], anchor="middle"))
    for n, s in enumerate(["picks up the comment", "reads the text and your style", "edits the .tex, writes a reply",
                           "compile-checks, publishes"]):
        b.append(f'<circle cx="358" cy="{146 + 25 * n}" r="3.5" fill="{c["tool"]}"/>' + t(370, 151 + 25 * n, s, 15))
    b.append(f'<path d="M626,159 L652,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 3. the page
    b.append(f'<path d="M658,34 H928 L950,56 V284 H658 Z" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
             f'<path d="M928,34 V56 H950" fill="{c["bar"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
             f'<rect x="674" y="50" width="190" height="7" rx="3" fill="{c["skel"]}"/>'
             f'<rect x="674" y="64" width="240" height="7" rx="3" fill="{c["skel"]}"/>')
    for n, s in enumerate(["Iterative preference optimization", "trains a policy on its own samples.",
                           "Each round it resets the reference",
                           'to the newest policy (<tspan class="i">reference</tspan>',
                           '<tspan class="i">refresh</tspan>), so the target moves.']):
        b.append(t(674, 96 + 20 * n, s, 15))
    b.append(f'<rect x="668" y="188" width="274" height="66" rx="4" fill="{c["note_soft"]}"/>')
    for n, s in enumerate([f'[c7] <tspan class="b">Ada:</tspan> too much jargon;',
                           f'define it before using it, max 5',
                           f'lines <tspan class="b">Claude:</tspan> Defined it. 5 lines.']):
        b.append(t(676, 207 + 19 * n, s, 14.3, c["note"]))
    b.append(f'<rect x="674" y="264" width="220" height="7" rx="3" fill="{c["skel"]}"/>')
    # 4. the style guide
    b.append(f'<rect x="340" y="318" width="282" height="64" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(badge(360, 337, "4", c))
    b.append(t(378, 343, "Your style guide", 17.5, c["gold_ink"], "b"))
    b.append(t(360, 368, "STYLE.md: plain text, in git", 14.5))
    b.append(f'<path d="M804,288 C804,340 720,350 626,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M156,288 C156,340 240,350 336,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M481,316 L481,252" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#ap)"/>')
    b.append(t(472, 290, "read before every edit", 14.5, c["tool"], anchor="end"))
    b.append(t(950, 381, "what you keep, rewrite or undo", 14.5, c["gold_ink"], anchor="end"))
    b.append(t(12, 381, "and what you write yourself", 14.5, c["gold_ink"]))
    b.append(t(950, 406, "Accept: delete the note. Follow up: comment under it.", 14.5, c["ink2"], anchor="end"))
    return svg(960, 414, "The PairTeX loop: you comment in your editor, the agent edits and replies, both land in the paper, "
               "and every round teaches your style guide", "\n".join(b), c)


# ------------------------------------------------------------------------------------------------------------ before/after

def versus(c: dict) -> str:
    b = []
    # left: chatbot
    b.append(f'<rect x="0" y="0" width="470" height="300" rx="8" fill="{c["wash"]}"/>'
             f'<rect x="0" y="0" width="470" height="4" fill="{c["grey"]}"/>')
    b.append(t(20, 36, "Writing with a chatbot", 18, c["ink2"], "b"))
    b.append(editor(20, 66, 154, 104, "paper.tex", c))
    for n in range(4):
        b.append(f'<rect x="36" y="{108 + 14 * n}" width="{[112, 90, 104, 66][n]}" height="6" rx="3" fill="{c["skel"]}"/>')
    # the chat window
    b.append(f'<rect x="306" y="66" width="140" height="104" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
             f'<rect x="318" y="82" width="90" height="20" rx="10" fill="{c["skel"]}"/>'
             f'<rect x="344" y="110" width="90" height="20" rx="10" fill="{c["skel"]}"/>'
             f'<rect x="318" y="138" width="74" height="20" rx="10" fill="{c["skel"]}"/>')
    b.append(f'<path d="M180,98 C218,74 264,74 300,98" stroke="{c["grey"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(f'<path d="M300,142 C264,166 218,166 180,142" stroke="{c["grey"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    b.append(t(240, 66, "copy, explain again", 13.5, c["ink2"], anchor="middle"))
    b.append(t(240, 190, "paste back, fix LaTeX", 13.5, c["ink2"], anchor="middle"))
    b.append(t(240, 125, "× every round", 14, c["bad"], "b", "middle"))
    for n, s in enumerate(["Each round trip breaks your train of thought.", "The drafts sound like the model.",
                           "It forgets every correction you made."]):
        y = 226 + 26 * n
        b.append(f'<circle cx="31" cy="{y - 5}" r="9" fill="{c["bad_soft"]}"/>'
                 f'<path d="M27,{y - 9} l8,8 M35,{y - 9} l-8,8" stroke="{c["bad"]}" stroke-width="2" stroke-linecap="round"/>')
        b.append(t(48, y, s, 15.5))
    # right: PairTeX
    b.append(f'<rect x="490" y="0" width="470" height="300" rx="8" fill="{c["tool_soft"]}"/>'
             f'<rect x="490" y="0" width="470" height="4" fill="{c["tool"]}"/>')
    b.append(t(510, 36, "With PairTeX", 18, c["tool"], "b"))
    b.append(editor(514, 66, 250, 104, "paper.tex", c))
    for n in range(2):
        b.append(f'<rect x="526" y="{108 + 14 * n}" width="{[200, 160][n]}" height="6" rx="3" fill="{c["skel"]}"/>')
    b.append(f'<text x="526" y="146" font-size="13" class="m" style="fill:{c["you"]}"><tspan class="b">%!</tspan> tighten this<tspan class="b">..</tspan></text>')
    b.append(f'<rect x="524" y="153" width="230" height="11" rx="3" fill="{c["note_soft"]}"/>'
             f'<rect x="530" y="156.5" width="150" height="4" rx="2" fill="{c["note"]}" opacity="0.55"/>')
    # the agent, in the background
    b.append(f'<circle cx="884" cy="116" r="34" fill="{c["paper"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(f'<path d="M870,106 h28 v20 h-28 z M876,100 v6 M892,100 v6 M877,115 h3 M888,115 h3 M878,121 h12" stroke="{c["tool"]}" '
             f'stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(t(884, 168, "the agent, in", 13.5, c["tool"], anchor="middle"))
    b.append(t(884, 184, "the background", 13.5, c["tool"], anchor="middle"))
    b.append(f'<path d="M770,104 C800,92 822,96 846,106" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="5 4" fill="none" marker-end="url(#ap)"/>')
    b.append(f'<path d="M846,130 C822,142 800,146 770,136" stroke="{c["note"]}" stroke-width="2" fill="none" marker-end="url(#an)"/>')
    for n, s in enumerate(["Comments live in the .tex file: no copy, no paste.", "You keep writing while the agent works.",
                           "It learns a style guide from your edits."]):
        y = 226 + 26 * n
        b.append(f'<circle cx="521" cy="{y - 5}" r="9" fill="{c["note_soft"]}"/>'
                 f'<path d="M516,{y - 5} l4,4 l7,-8" stroke="{c["note"]}" stroke-width="2" fill="none" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
        b.append(t(538, y, s, 15.5))
    return svg(960, 300, "Writing with a chatbot means copying text out and pasting it back every round; with PairTeX the "
               "comment stays in the .tex file and the agent answers in the background", "\n".join(b), c)


# ------------------------------------------------------------------------------------------------------------ comments

def comments(c: dict) -> str:
    b = [editor(0, 0, 520, 246, "main.tex", c)]
    cw = 8.73  # Menlo at 14.5 px; Consolas is a little narrower
    y0, dy = 64, 26
    rows = [
        ("1", "The policy converges when the gain"),
        ("2", 'is small. <tspan class="b">%?</tspan> proved, or only observed?<tspan class="b">..</tspan>'),
        ("3", ""),
        ("4", 'We study the loop. <tspan class="b">[[</tspan>One round is'),
        ("5", 'one mirror step.<tspan class="b">]]</tspan> The target moves.'),
        ("6", '<tspan class="b">%!</tspan> too much jargon; define the'),
        ("7", '%  target first, under five lines<tspan class="b">..</tspan>'),
    ]
    def hl(row, col, n, rows=1):
        return (f'<rect x="{42 + col * cw - 3:.1f}" y="{y0 + dy * row - 17}" width="{n * cw + 6:.1f}" '
                f'height="{23 + dy * (rows - 1)}" rx="3" fill="{c["you_soft"]}"/>')
    b += [hl(1, 10, 30), hl(3, 19, 14), hl(4, 0, 18), hl(5, 0, 35, 2)]
    for n, (num, s) in enumerate(rows):
        y = y0 + dy * n
        b.append(t(14, y, num, 13, c["ink2"], "m"))
        if s:
            col = c["you"] if n in (5, 6) else None
            b.append(t(42, y, s, 14.5, col, "m"))
    # callouts
    calls = [
        (y0 + dy + 3, "%? … ..", "A question", "The agent answers in a note, changes no text"),
        (y0 + 3.5 * dy, "[[ … ]]", "Point at words", "even across lines; the brackets go later"),
        (y0 + 5.5 * dy + 6, "%! … ..", "A change request", "The agent edits the text and replies"),
    ]
    for y, code, head, sub in calls:
        b.append(f'<path d="M522,{y - 5} L566,{y - 5}" stroke="{c["you"]}" stroke-width="1.6" fill="none"/>'
                 f'<circle cx="566" cy="{y - 5}" r="3" fill="{c["you"]}"/>')
        b.append(t(578, y - 8, f'<tspan class="m b" style="fill:{c["you"]}">{code}</tspan>  <tspan class="b">{head}</tspan>', 16))
        b.append(t(578, y + 13, sub, 14.5, c["ink2"]))
    b.append(t(578, 262, f'<tspan class="m b" style="fill:{c["you"]}">..</tspan>  <tspan class="b">sends it.</tspan>', 16))
    b.append(t(578, 283, "Take your time over several lines; … is an ellipsis.", 14.5, c["ink2"]))
    # then: chips
    b.append(t(0, 326, "Then, in the same file:", 16, None, "b"))
    chips = [("Accept", "delete the note"), ("Push back", "comment under it"), ("Undo", "%! revert this.."),
             ("Choose", "%! 2..")]
    x = 0
    widths = [218, 238, 222, 150]
    for (k, v), w in zip(chips, widths):
        mono = v.startswith("%")
        b.append(f'<rect x="{x}" y="340" width="{w}" height="34" rx="17" fill="{c["wash"]}" stroke="{c["rule"]}" stroke-width="1.2"/>')
        val = f'<tspan class="m" style="fill:{c["you"]}">{v}</tspan>' if mono else v
        b.append(t(x + 16, 362, f'<tspan class="b">{k}</tspan>  {val}', 14.5))
        x += w + 12
    return svg(960, 380, "Comment syntax: %? asks a question, %! asks for a change, double brackets point at words, two dots "
               "send the comment; then accept, push back, undo or choose in the same file", "\n".join(b), c)


# --------------------------------------------------------------------------------------------------------------- style

def style(c: dict) -> str:
    b = [t(10, 18, "What you do", 15.5, c["ink2"])]
    acts = [("You rewrite", "the agent’s text", "strongest"), ("You undo", "an edit", "never again"),
            ("You state", "a preference", "“always …”"), ("You write", "on your own", "style, not content"),
            ("You keep", "an edit", "confirms a rule")]
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
    b.append(t(498, 189, "its word diff", 14.5, c["ink2"], anchor="middle"))
    b.append(f'<path d="M580,161 L606,161" stroke="{c["grey"]}" stroke-width="1.6" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="612" y="12" width="346" height="282" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(t(630, 40, "STYLE.md", 17, c["gold_ink"], "b"))
    b.append(t(940, 40, "yours to edit", 14.5, c["gold_ink"], anchor="end"))
    b.append(f'<line x1="630" y1="50" x2="940" y2="50" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    rows = [(76, "Base rules", "only you add these"), (108, "Confirmed rules", "3 pieces of evidence"),
            (196, "Tentative patterns", "seen once or twice"), (226, "Words: prefer / avoid", ""),
            (256, "What you undid", "never repeated")]
    for y, k, v in rows:
        b.append(t(630, y, k, 15.5, None, "b"))
        if v:
            b.append(t(940, y, v, 14.5, c["ink2"], anchor="end"))
    b.append(f'<rect x="630" y="118" width="310" height="52" rx="4" fill="{c["paper"]}" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    b.append(t(640, 139, "e.g. Open each paragraph with its", 14.5, cls="i"))
    b.append(t(640, 159, "claim; the setup comes after it.", 14.5, cls="i"))
    b.append(t(630, 282, "Every change is a git commit you can undo.", 14.5, c["ink2"]))
    b.append(f'<path d="M784,298 C784,318 704,322 622,322" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" '
             f'fill="none" marker-end="url(#ap)"/>')
    b.append(t(614, 327, "the agent reads it before every edit", 15, c["tool"], anchor="end"))
    return svg(960, 336, "How the style guide learns: your rewrites, undos, stated preferences, own writing and kept edits "
               "become evidence, distilled into STYLE.md, which the agent reads before every edit", "\n".join(b), c)


# ------------------------------------------------------------------------------------------------------------ features

ICONS = {
    "where": '<rect x="6" y="9" width="36" height="28" rx="3"/><path d="M16 43h16M24 37v6M13 18l5 5-5 5M22 28h10"/>',
    "people": '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="16" r="6"/>'
              '<path d="M6 40c0-7 5-12 11-12s11 5 11 12M24 31c2-2 5-3 9-3 6 0 11 5 11 12"/>',
    "shield": '<path d="M24 5l15 6v11c0 10-6 17-15 21C15 39 9 32 9 22V11z"/><path d="M17 24l5 5 9-10"/>',
    "doc": '<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9M18 27l5 5 8-9"/>',
}


def features(c: dict) -> str:
    cards = [
        ("where", "you", "Works where you write",
         ['<tspan class="b">Overleaf</tspan>, through its git integration',
          '<tspan class="b">GitHub, GitLab</tspan> or any git remote',
          '<tspan class="b">A local folder</tspan>: VS Code, TeXstudio, Emacs',
          '<tspan class="b">Any agent</tspan>: Claude Code, Codex, …']),
        ("people", "tool", "Several authors, several loops",
         ["Each loop answers only its owner’s comments",
          f'Ids carry the owner’s prefix: <tspan class="m" style="fill:{c["tool"]}">ada7</tspan>, '
          f'<tspan class="m" style="fill:{c["tool"]}">grace3</tspan>',
          "Each loop learns only from its owner’s edits",
          "Coauthors without a loop can be answered too"]),
        ("shield", "note", "Safe by default",
         ["A compile check before every publish",
          "Never adds files or deletes a thread unasked",
          "Your typing wins: it redoes its edit on yours",
          f'Every change is a commit: <tspan class="m" style="fill:{c["note"]}">pairtex: c7: …</tspan>']),
        ("doc", "gold_ink", "Ready for submission",
         [f'<tspan class="m" style="fill:{c["gold_ink"]}">pairtex check</tspan> lists what is left in the paper',
          f'<tspan class="m" style="fill:{c["gold_ink"]}">pairtex clean</tspan> writes a copy without it',
          "It drops % comments too: arXiv shows your source",
          "One switch hides every note in the PDF"]),
    ]
    b = []
    for n, (icon, col, head, items) in enumerate(cards):
        x, y = (n % 2) * 486, (n // 2) * 180
        b.append(f'<rect x="{x}" y="{y}" width="474" height="168" rx="8" fill="{c["paper"]}" stroke="{c["rule"]}" stroke-width="1.2"/>'
                 f'<path d="M{x},{y + 8} a8,8 0 0 1 8,-8 h458 a8,8 0 0 1 8,8 v-4 h-474 Z" fill="{c[col]}"/>')
        b.append(f'<g transform="translate({x + 18},{y + 18}) scale(0.58)" fill="none" stroke="{c[col]}" stroke-width="3" '
                 f'stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>')
        b.append(t(x + 54, y + 39, head, 18, c[col], "b"))
        for k, s in enumerate(items):
            yy = y + 72 + 26 * k
            b.append(f'<circle cx="{x + 24}" cy="{yy - 5}" r="3" fill="{c[col]}"/>' + t(x + 36, yy, s, 15))
    return svg(960, 348, "Built for real papers: works where you write, several authors with several loops, safe by "
               "default, ready for submission", "\n".join(b), c)


FIGURES = {"banner": banner, "loop": loop, "versus": versus, "comments": comments, "style": style, "features": features}

if __name__ == "__main__":
    for name, fn in FIGURES.items():
        (HERE / f"{name}.svg").write_text(fn(LIGHT), encoding="utf-8")
        (HERE / f"{name}-dark.svg").write_text(fn(DARK), encoding="utf-8")
        print(f"wrote {name}.svg, {name}-dark.svg")
