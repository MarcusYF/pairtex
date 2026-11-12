#!/usr/bin/env python3
"""Draw the suite README's figures and the tab bar: each as NAME.svg (light) and NAME-dark.svg (dark), for GitHub's <picture>.

Run: python3 docs/figures/make_figures.py
Same visual language as each tool's figures: blue is the author, purple the agent, green what the author's coauthors and
readers see, gold the style vault. System fonts (CMU Serif if installed, else Georgia), so lines are broken by hand.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ptfig", HERE.parent.parent / "pairtex" / "docs" / "figures" / "make_figures.py")
_pt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pt)
LIGHT, DARK, svg, badge, t = _pt.LIGHT, _pt.DARK, _pt.svg, _pt.badge, _pt.t

TOOLS = [  # key, name, verb, where the feedback lives, what comes out
    ("pairdeck", "PairDeck", "report what you found", ["comments on a slide,", "in your browser"],
     ["an animated HTML deck", "that explains one idea"]),
    ("pairtex", "PairTeX", "write the paper", ["%! comments in", "your LaTeX source"],
     ["the paper, on Overleaf,", "git or a folder"]),
    ("pairtalk", "PairTalk", "give the talk", ["comments on the talk site", "and script edits"],
     ["a talk with builds and", "a speaker script"]),
]


def wordmark(x: float, y: float, name: str, size: float, c: dict, anchor: str = "start") -> str:
    """Pair + the tool part in the agent's colour (PairTeX keeps its TeX logo)."""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    if name == "PairTeX":
        d = size * 0.115
        return (f'<text x="{x}" y="{y}" font-size="{size}" class="b"{a}>Pair<tspan style="fill:{c["tool"]}">T</tspan>'
                f'<tspan dx="-{d:.1f}" dy="{size * 0.2:.1f}" style="fill:{c["tool"]}">E</tspan>'
                f'<tspan dx="-{d:.1f}" dy="-{size * 0.2:.1f}" style="fill:{c["tool"]}">X</tspan></text>')
    return f'<text x="{x}" y="{y}" font-size="{size}" class="b"{a}>Pair<tspan style="fill:{c["tool"]}">{name[4:]}</tspan></text>'


# ------------------------------------------------------------------------------------------------------------- banner

def banner(c: dict) -> str:
    body = [
        t(4, 26, "OPEN SOURCE  ·  MIT LICENSE  ·  FOR RESEARCHERS", 13.5, c["ink2"], extra=' letter-spacing="2.2"'),
        wordmark(0, 104, "PairLab", 78, c),
        f'<text x="2" y="150" font-size="25">Research tools that <tspan class="b" style="fill:{c["gold_ink"]}">learn your '
        f'style</tspan>: pair-explain, pair-write, pair-present.</text>',
        f'<rect x="2" y="168" width="170" height="3" fill="{c["gold"]}"/>',
    ]
    return svg(960, 180, "PairLab: research tools that learn your style: pair-explain, pair-write, pair-present",
               "\n".join(body), c)


# ----------------------------------------------------------------------------------------------------------- workflow

def workflow(c: dict) -> str:
    b = []
    xs = [10, 330, 650]
    w = 300
    for n, (x, (_, name, verb, where, out)) in enumerate(zip(xs, TOOLS)):
        b.append(badge(x + 12, 16, str(n + 1), c))
        b.append(t(x + 30, 22, verb[0].upper() + verb[1:], 17, None, "b"))
        b.append(f'<rect x="{x}" y="38" width="{w}" height="236" rx="10" fill="{c["paper"]}" stroke="{c["line"]}" stroke-width="1.6"/>')
        b.append(wordmark(x + w / 2, 84, name, 34, c, "middle"))
        b.append(f'<line x1="{x + 24}" y1="104" x2="{x + w - 24}" y2="104" stroke="{c["rule"]}" stroke-width="1.2"/>')
        b.append(t(x + 22, 132, "You give feedback", 14.5, c["ink2"]))
        b += [t(x + 22, 155 + 21 * k, s, 16, c["you"]) for k, s in enumerate(where)]
        b.append(t(x + 22, 214, "Your agent delivers", 14.5, c["ink2"]))
        b += [t(x + 22, 237 + 21 * k, s, 16, c["tool"]) for k, s in enumerate(out)]
        if n < 2:
            b.append(f'<path d="M{x + w + 4},156 L{x + w + 24},156" stroke="{c["ink2"]}" stroke-width="2" fill="none" marker-end="url(#a)"/>')
        b.append(f'<path d="M{x + w / 2},{344} L{x + w / 2},{280}" stroke="{c["tool"]}" stroke-width="2" stroke-dasharray="6 5" '
                 f'fill="none" marker-end="url(#ap)"/>')
    b.append(f'<rect x="10" y="348" width="940" height="74" rx="10" fill="{c["gold_soft"]}" stroke="{c["gold"]}" stroke-width="1.8"/>')
    b.append(t(30, 377, "Your style vault, one per tool", 17.5, c["gold_ink"], "b"))
    b.append(t(30, 403, "seeded from your own papers, decks and talks; grows with every edit you keep, rewrite or undo", 15.5))
    b.append(t(940, 377, "read before every piece of work", 14.5, c["tool"], anchor="end"))
    b.append(f'<rect x="10" y="436" width="940" height="44" rx="10" fill="{c["tool_soft"]}" stroke="{c["tool"]}" stroke-width="1.6"/>')
    b.append(f'<text x="480" y="464" font-size="16" text-anchor="middle"><tspan class="b" style="fill:{c["tool"]}">Your agent</tspan>'
             f' does the thinking: Claude Code, Codex, or any agent that runs shell commands, on your own plan</text>')
    return svg(960, 488, "Three moments of research, three tools: PairDeck reports what you found, PairTeX writes the paper, "
               "PairTalk gives the talk. Each keeps a style vault, seeded from your own work and grown from your feedback, and "
               "runs in the coding agent you already use", "\n".join(b), c)


# ----------------------------------------------------------------------------------------------------------- promises

def promises(c: dict) -> str:
    cards = [
        ("It learns you", c["gold"], c["gold_soft"], c["gold_ink"],
         ["A style guide per tool, in plain", "text, in git, in your home folder.", "Every edit you keep, rewrite or",
          "undo is evidence; three pieces", "confirm a rule. Your edits win."]),
        ("You stay in flow", c["you"], c["you_soft"], c["you"],
         ["Feedback goes where the work is:", "the .tex source, the slide, the", "script. Your agent picks it up in",
          "the background, fixes it, replies", "next to it and publishes."]),
        ("Starts from your work", c["tool"], c["tool_soft"], c["tool"],
         ["Seed each guide from papers,", "decks and talks you already made,", "so the first draft sounds and",
          "looks like you. It runs on your", "Claude or ChatGPT plan: no API key."]),
    ]
    b = []
    for n, (title, col, soft, ink, lines) in enumerate(cards):
        x = 10 + 320 * n
        b.append(f'<rect x="{x}" y="6" width="300" height="214" rx="10" fill="{soft}" stroke="{col}" stroke-width="1.8"/>')
        b.append(badge(x + 26, 36, str(n + 1), c))
        b.append(t(x + 46, 42, title, 19, ink, "b"))
        b += [t(x + 22, 78 + 26 * k, s, 16) for k, s in enumerate(lines)]
    return svg(960, 228, "What the three tools share: they learn your style; you stay in flow while the agent works in the "
               "background; each starts from your own past work and runs on your own agent plan", "\n".join(b), c)


# --------------------------------------------------------------------------------------------------------------- tabs

TABS = [("overview", "PairLab", "the suite"), ("pairdeck", "PairDeck", "report"), ("pairtex", "PairTeX", "write"),
        ("pairtalk", "PairTalk", "present")]


def tab(key: str, name: str, sub: str, on: bool, c: dict) -> str:
    w, h = 200, 64
    b = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="{c["gold_soft"] if on else c["paper"]}"/>',
         f'<rect x="0" y="{h - (5 if on else 1.5)}" width="{w}" height="{5 if on else 1.5}" fill="{c["gold"] if on else c["line"]}"/>']
    if on:
        b.append(wordmark(w / 2, 32, name, 23, c, "middle"))
    else:
        b.append(f'<text x="{w / 2}" y="32" font-size="23" class="b" text-anchor="middle" style="fill:{c["ink2"]}">{name}</text>')
    b.append(t(w / 2, 52, sub, 14.5, c["gold_ink"] if on else c["grey"], anchor="middle"))
    return svg(w, h, f"{name}: {sub}" + (" (this page)" if on else ""), "\n".join(b), c)


def tabbar_html(here: str, prefix: str) -> str:
    """The tab bar as README HTML: one linked image per tab, no whitespace between them so they touch."""
    pages = {"overview": "README.md", "pairdeck": "pairdeck/README.md", "pairtex": "pairtex/README.md",
             "pairtalk": "pairtalk/README.md"}
    cells = []
    for key, name, sub in TABS:
        state = "on" if key == here else "off"
        src = f"{prefix}docs/figures/tab-{key}-{state}"
        cells.append(f'<a href="{prefix}{pages[key]}"><picture><source media="(prefers-color-scheme: dark)" srcset="{src}-dark.svg">'
                     f'<img src="{src}.svg" width="200" alt="{name}: {sub}"></picture></a>')
    return '<p align="center">' + "".join(cells) + "</p>"


def inject_tabbars() -> list[str]:
    """Put the tab bar into each README, between <!-- TABBAR --> and <!-- /TABBAR --> (a lone <!-- TABBAR --> is filled)."""
    import re
    root = HERE.parent.parent
    done = []
    for key, readme in (("overview", root / "README.md"), ("pairdeck", root / "pairdeck" / "README.md"),
                        ("pairtex", root / "pairtex" / "README.md"), ("pairtalk", root / "pairtalk" / "README.md")):
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8")
        block = "<!-- TABBAR -->\n" + tabbar_html(key, "" if key == "overview" else "../") + "\n<!-- /TABBAR -->"
        new = re.sub(r"<!-- TABBAR -->(?:.*?<!-- /TABBAR -->)?", lambda m: block, text, count=1, flags=re.S)
        if new != text:
            readme.write_text(new, encoding="utf-8")
            done.append(str(readme.relative_to(root)))
    return done


def main() -> None:
    figs = {"banner": banner, "workflow": workflow, "promises": promises}
    for name, fn in figs.items():
        (HERE / f"{name}.svg").write_text(fn(LIGHT), encoding="utf-8")
        (HERE / f"{name}-dark.svg").write_text(fn(DARK), encoding="utf-8")
    for key, name, sub in TABS:
        for on in (True, False):
            stem = f"tab-{key}-{'on' if on else 'off'}"
            (HERE / f"{stem}.svg").write_text(tab(key, name, sub, on, LIGHT), encoding="utf-8")
            (HERE / f"{stem}-dark.svg").write_text(tab(key, name, sub, on, DARK), encoding="utf-8")
    (HERE / "tabbar.txt").write_text("\n".join(f"{key}: {tabbar_html(key, '' if key == 'overview' else '../')}"
                                               for key, _, _ in TABS) + "\n", encoding="utf-8")
    print(f"wrote {len(figs) * 2 + len(TABS) * 4} figures and tabbar.txt in {HERE}")
    for readme in inject_tabbars():
        print(f"tab bar in {readme}")


if __name__ == "__main__":
    main()
