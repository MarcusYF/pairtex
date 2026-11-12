#!/usr/bin/env python3
"""Draw the README figures: each as NAME.svg (light) and NAME-dark.svg (dark), for GitHub's <picture> switch.

Run: python3 docs/figures/make_figures.py
The visual language is PairTeX's (pairtex/docs/figures/make_figures.py): blue is the author, purple the agent, green the
replies as they show, gold the style guide. Figures use system fonts (CMU Serif if installed, else Georgia), so every line is
broken by hand and kept short; no text is smaller than 15 units.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

LIGHT = dict(ink="#232323", ink2="#6B6B6B", line="#BDBDBD", rule="#D9D9D9", wash="#F6F6F4", bar="#F1F1EE",
             skel="#E4E4E1", paper="#FFFFFF", dot="#D9D9D9", grey="#9A9A9A",
             you="#27709C", you_soft="#EAF2F8", tool="#6D5398", tool_soft="#F3EEF8", note="#227828", note_soft="#EDF5EC",
             gold="#C6952C", gold_ink="#8A6410", gold_soft="#FBF6E9", gold_line="#E5D3A6", on_gold="#FFFFFF",
             bad="#B4463C", bad_soft="#FBEDEB", box="#25887E", box_soft="#E3F1EF")
DARK = dict(ink="#E6EDF3", ink2="#9198A1", line="#3D444D", rule="#30363D", wash="#161B22", bar="#21262D",
            skel="#30363D", paper="#161B22", dot="#484F58", grey="#7D8590",
            you="#5AA8DA", you_soft="#0F2536", tool="#B39DDB", tool_soft="#231C33", note="#5DBB63", note_soft="#12261A",
            gold="#D4A33A", gold_ink="#E3B95A", gold_soft="#261E0F", gold_line="#5A4520", on_gold="#0D1117",
            bad="#E5786D", bad_soft="#2D1614", box="#4FB3A8", box_soft="#0F2522")

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
    """A browser window with a title bar: the talk on the review server or the shared site."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>'
            f'<path d="M{x},{y + 8} a8,8 0 0 1 8,-8 h{w - 16} a8,8 0 0 1 8,8 v22 h-{w} Z" fill="{c["bar"]}"/>'
            f'<circle cx="{x + 17}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/><circle cx="{x + 32}" cy="{y + 15}" r="4.5" '
            f'fill="{c["dot"]}"/><circle cx="{x + 47}" cy="{y + 15}" r="4.5" fill="{c["dot"]}"/>'
            + t(x + 66, y + 20, name, 15, c["ink2"], "m"))


def mini_chart(x, y, c, labelled=False) -> str:
    """A small slide: a title, a falling measured line, a dashed guarantee, and (after the fix) its label."""
    b = [f'<rect x="{x + 34}" y="{y}" width="150" height="8" rx="4" fill="{c["skel"]}"/>',
         f'<path d="M{x + 14},{y + 26} V{y + 128} H{x + 214}" stroke="{c["ink2"]}" stroke-width="1.6" fill="none"/>',
         f'<path d="M{x + 16},{y + 34} L{x + 200},{y + 64}" stroke="{c["gold"]}" stroke-width="2.4" stroke-dasharray="7 5" fill="none"/>',
         f'<path d="M{x + 16},{y + 34} L{x + 44},{y + 56} L{x + 70},{y + 66} L{x + 98},{y + 84} L{x + 126},{y + 92} '
         f'L{x + 156},{y + 108} L{x + 196},{y + 118}" stroke="{c["you"]}" stroke-width="2.4" fill="none"/>']
    if labelled:
        b.append(t(x + 200, y + 52, "guarantee", 15, c["gold"], anchor="end"))
    return "".join(b)


# ------------------------------------------------------------------------------------------------------------- banner

def banner(c: dict) -> str:
    body = [
        t(4, 26, "OPEN SOURCE  ·  MIT LICENSE  ·  FOR RESEARCH TALKS", 13.5, c["ink2"], extra=' letter-spacing="2.2"'),
        f'<text x="0" y="104" font-size="78" class="b" letter-spacing="-1">Pair<tspan style="fill:{c["tool"]}">Talk</tspan></text>',
        f'<text x="2" y="150" font-size="25">Talk slides your <tspan class="b" style="fill:{c["tool"]}">AI coauthor</tspan> '
        f'fixes from comments, in the way you present.</text>',
        f'<rect x="2" y="168" width="170" height="3" fill="{c["gold"]}"/>',
    ]
    return svg(960, 180, "PairTalk: talk slides your AI coauthor fixes from comments, in the way you present",
               "\n".join(body), c)


# --------------------------------------------------------------------------------------------------------------- loop

def loop(c: dict) -> str:
    b = []
    b += [badge(22, 14, "1", c), t(40, 20, "You comment on a slide", 17, c["you"], "b"),
          badge(352, 14, "2", c), t(370, 20, "The agent fixes it", 17, c["tool"], "b"),
          badge(662, 14, "3", c), t(680, 20, "The fix and the reply land", 17, None, "b")]
    # 1. the talk in the browser, with a box and a comment
    b.append(window(10, 34, 292, 250, "localhost · mytalk", c))
    b.append(mini_chart(30, 76, c))
    b.append(f'<rect x="168" y="94" width="94" height="44" rx="3" fill="{c["box_soft"]}" fill-opacity="0.6" '
             f'stroke="{c["box"]}" stroke-width="2"/>')
    b.append(f'<rect x="22" y="212" width="268" height="62" rx="6" fill="{c["you_soft"]}"/>')
    b.append(t(32, 233, '<tspan class="b">Ada</tspan> · slide 8, click 2, box', 15, c["you"]))
    b.append(t(32, 255, "What does the dashed line", 15))
    b.append(t(32, 271, "guarantee? Say it in words.", 15))
    b.append(f'<path d="M306,159 L334,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 2. the agent
    b.append(f'<rect x="340" y="62" width="282" height="196" rx="8" fill="{c["tool_soft"]}" stroke="{c["tool"]}" stroke-width="1.8"/>')
    b.append(t(481, 91, "Your agent + pairtalk", 17.5, c["tool"], "b", "middle"))
    b.append(t(481, 111, "(Claude Code, Codex, …)", 14.5, c["ink2"], anchor="middle"))
    for n, s in enumerate(["gets the slide, click and box", "reads your talk style", "edits the slide and the script",
                           "screenshots every click", "replies under your comment"]):
        b.append(f'<circle cx="358" cy="{136 + 24 * n}" r="3.5" fill="{c["tool"]}"/>' + t(370, 141 + 24 * n, s, 15))
    b.append(f'<path d="M626,159 L652,159" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    # 3. the slide, fixed, and the reply
    b.append(window(658, 34, 292, 250, "localhost · mytalk", c))
    b.append(mini_chart(678, 76, c, labelled=True))
    b.append(f'<rect x="670" y="212" width="268" height="62" rx="6" fill="{c["note_soft"]}"/>')
    b.append(t(680, 233, '<tspan class="b">Reply</tspan> · done', 15, c["note"]))
    b.append(t(680, 255, "Labelled it “guarantee”; the", 15, c["note"]))
    b.append(t(680, 271, "script says why it is loose.", 15, c["note"]))
    # 4. the style guide
    b.append(f'<rect x="340" y="318" width="282" height="64" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(badge(360, 337, "4", c))
    b.append(t(378, 343, "Your talk style", 17.5, c["gold_ink"], "b"))
    b.append(t(360, 368, "STYLE.md: plain text, in git", 14.5))
    b.append(f'<path d="M804,288 C804,340 720,350 626,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M156,288 C156,340 240,350 336,350" stroke="{c["gold"]}" stroke-width="2.4" fill="none" marker-end="url(#ag)"/>')
    b.append(f'<path d="M481,316 L481,262" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#ap)"/>')
    b.append(t(472, 296, "read before every slide", 14.5, c["tool"], anchor="end"))
    b.append(t(950, 381, "what you keep, rewrite or undo", 14.5, c["gold_ink"], anchor="end"))
    b.append(t(12, 381, "what you say “always” about", 14.5, c["gold_ink"]))
    b.append(t(950, 406, "Coauthors comment too: fixed and answered, never learned.", 14.5, c["ink2"], anchor="end"))
    return svg(960, 414, "The PairTalk loop: you comment on a slide and click, the agent fixes the slide and the script and "
               "replies, the fix and the reply show in the talk, and every round teaches your talk-style guide",
               "\n".join(b), c)


# --------------------------------------------------------------------------------------------------------------- style

def style(c: dict) -> str:
    b = [t(10, 18, "Where the evidence comes from", 15.5, c["ink2"])]
    acts = [("You rewrite", "the agent’s script", "strongest"), ("You undo", "a change", "never again"),
            ("You say", "“always …”", "a rule at once"), ("You edit", "your own notes", "your habits"),
            ("Your past talks", "", "seed")]
    for n, (v, rest, tag) in enumerate(acts):
        y = 30 + 50 * n
        seed = n == 4
        fill, line = (c["gold_soft"], c["gold"]) if seed else (c["you_soft"], c["you"])
        b.append(f'<rect x="10" y="{y}" width="340" height="42" rx="6" fill="{fill}" stroke="{line}" stroke-width="1.6"/>')
        b.append(t(24, y + 27, f'<tspan class="b">{v}</tspan> {rest}', 16))
        b.append(t(338, y + 27, tag, 14.5, c["gold_ink"] if seed else c["you"], "i", "end"))
        b.append(f'<path d="M352,{y + 21} C380,{y + 21} 380,151 404,151" stroke="{c["grey"]}" stroke-width="1.6" fill="none"/>')
    # coauthors: fixed, not learned
    b.append(f'<rect x="10" y="286" width="340" height="42" rx="6" fill="{c["wash"]}" stroke="{c["grey"]}" '
             f'stroke-width="1.4" stroke-dasharray="5 4"/>')
    b.append(t(24, 313, '<tspan class="b">A coauthor</tspan> comments', 16, c["ink2"]))
    b.append(t(338, 313, "fixed, not learned", 14.5, c["ink2"], "i", "end"))
    b.append(f'<path d="M404,151 L414,151" stroke="{c["grey"]}" stroke-width="1.6" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="418" y="108" width="160" height="86" rx="6" fill="{c["wash"]}" stroke="{c["grey"]}" stroke-width="1.6"/>')
    b.append(t(498, 138, "Evidence log", 16, None, "b", "middle"))
    b.append(t(498, 160, "each event with", 14.5, c["ink2"], anchor="middle"))
    b.append(t(498, 179, "its before and after", 14.5, c["ink2"], anchor="middle"))
    b.append(f'<path d="M580,151 L606,151" stroke="{c["grey"]}" stroke-width="1.6" fill="none" marker-end="url(#a)"/>')
    b.append(f'<rect x="612" y="12" width="346" height="316" rx="8" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(t(630, 40, "STYLE.md", 17, c["gold_ink"], "b"))
    b.append(t(940, 40, "yours to edit", 14.5, c["gold_ink"], anchor="end"))
    b.append(f'<line x1="630" y1="50" x2="940" y2="50" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    rows = [(76, "Base rules", "only you add these"), (102, "Confirmed rules", "3 pieces of evidence"),
            (128, "Tentative patterns", "seen once or twice"), (154, "Pacing and script", "")]
    for y, k, v in rows:
        b.append(t(630, y, k, 15.5, None, "b"))
        if v:
            b.append(t(940, y, v, 14.5, c["ink2"], anchor="end"))
    b.append(f'<rect x="630" y="164" width="310" height="76" rx="4" fill="{c["paper"]}" stroke="{c["gold_line"]}" stroke-width="1.2"/>')
    for n, (k, v) in enumerate([("pace", "135 words a minute (seed)"), ("opening", "a question, then the claim"),
                                ("hand-over", "one bridge line per slide")]):
        b.append(t(642, 186 + 22 * n, k, 15, c["ink2"]) + t(738, 186 + 22 * n, v, 15, cls="i"))
    b.append(t(630, 264, "What you undid", 15.5, None, "b"))
    b.append(t(940, 264, "never repeated", 14.5, c["ink2"], anchor="end"))
    b.append(t(630, 296, "Every change is a git commit you can undo.", 14.5, c["ink2"]))
    b.append(f'<path d="M784,332 C784,350 704,354 622,354" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" '
             f'fill="none" marker-end="url(#ap)"/>')
    b.append(t(614, 359, "the agent reads it before every slide", 15, c["tool"], anchor="end"))
    return svg(960, 368, "How the talk-style guide learns: your rewrites of the agent's script, your undos, what you say "
               "always about, your own notes and your past talks become evidence, distilled into STYLE.md with a Pacing and "
               "script table; coauthors' comments are fixed but never learned", "\n".join(b), c)


FIGURES = {"banner": banner, "loop": loop, "style": style}

if __name__ == "__main__":
    for name, fn in FIGURES.items():
        (HERE / f"{name}.svg").write_text(fn(LIGHT), encoding="utf-8")
        (HERE / f"{name}-dark.svg").write_text(fn(DARK), encoding="utf-8")
        print(f"wrote {name}.svg, {name}-dark.svg")
