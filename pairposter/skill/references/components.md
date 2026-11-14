# The poster engine: markup

`new` writes this skeleton; keep its outer structure (the overlay and the checks rely on the class names).

```html
<meta name="pairposter" content='{"width_mm": 1400, "height_mm": 900, "min_pt": 24, "fine_pt": 20, "words": 250, "block_words": 45}'>
...
<div class="pp-view dk-deck"><div class="pp-sizer">
<article class="pp-poster dk-slide is-current" data-label="Poster"><div class="pp-stage dk-inner">
  <header class="pp-head" data-label="Title"> .pp-titles (h1.pp-title.dk-h, .pp-authors, .pp-affil, .pp-venue) + .pp-logos </header>
  <div class="pp-body"> three .pp-col, each holding .pp-block sections </div>
  <footer class="pp-foot"> .pp-take (the takeaway band) + optional presenter card </footer>
</div></article>
</div></div>
<svg class="pp-sprite">…</svg>   <!-- the icon sprite, inlined by `new` -->
```

- `meta name="pairposter"`: the page size in mm (the venue's maximum), the type floor `min_pt` and the fine-print floor
  `fine_pt`, and the word budgets `qa` checks.
- **`data-label`** on every block (and on any part a comment might be about): the review page names the block under a
  comment's box with it, and `qa` reports by it.
- Columns: set `grid-template-columns` on `.pp-body` in the page's `<style>` (e.g. `1fr 1.08fr 1fr`).

## Tokens

Override in the page's `<style>` on `:root`: `--accent`, `--accent-2`, `--accent-soft`, `--wash`, `--line`, `--ink`,
`--muted`, `--good`, `--bad`, series colours `--c1`…`--c4`; type `--fs-title`, `--fs-h`, `--fs-big`, `--fs-body`, `--fs-small`,
`--fs-fine`, `--fs-stat`, all in pt; spacing `--pad`, `--gap`, `--inner`, `--radius` in mm. Use the tokens; do not hard-code
colours in blocks.

## Blocks

```html
<section class="pp-block pp-grow pp-spread" data-label="Model">
  <h2 class="pp-h"><span class="pp-num">2</span>Setting: who acts, what flows</h2>
  …
</section>
```

`.pp-grow` fills the column's spare height; `.pp-spread` spreads it between the block's parts. `.pp-tint` (a wash, no border)
and `.pp-accent` (accent background) vary a block. `.pp-lead` is a large line (a question, a claim).

## Pieces

| Class | What it is |
| --- | --- |
| `.pp-chain` (`.pp-v` vertical) | Steps (`.pp-step`: a `.pp-disc` icon and a `.pp-t` phrase) with `svg.pp-arrow` between |
| `.pp-cards` (`style="--n: 3"`) | Cards (`.pp-card`: `.pp-k` key with an icon, `.pp-t` phrase) |
| `.pp-list` | Icon rows: `<li><svg class="pp-ico"><use href="#check"/></svg><span class="pp-t">phrase</span><span class="tag pp-fine">Thm 4.1</span></li>` |
| `.pp-stats` | Big numbers: `.pp-stat` with `.pp-n` and `.pp-t` |
| `.pp-eq` (`.pp-plain` without the wash) | A display formula, `$$…$$` |
| `.pp-fig` + `.pp-cap` | A figure (inline SVG chart or an img) and a caption of a few words |
| `.pp-chips` / `.pp-chip` | Tags |
| `.pp-take` | The takeaway band |
| `.pp-qr` | A QR card: `<div class="pp-qr"><img src="img/qr_paper.svg" alt="…"><span class="pp-t">Paper</span></div>` |
| `.pp-fine` | Fine print (captions, tags, affiliations): its own floor `fine_pt` |
| `.pp-row` (`.pp-top`, `.pp-even`), `.pp-stack`, `.pp-center`, `.pp-muted`, `.pp-hl`, `.pp-good`, `.pp-bad` | Layout and emphasis |

Text in `span`s that a comment may point at gets the class `.pp-t`, so the review page can quote it.

## Icons

`<svg class="pp-ico"><use href="#search"/></svg>`; `.pp-lg`, `.pp-xl` for larger; inside `.pp-disc` for a round badge. The
sprite holds PairDeck's icons (person, robot, creator, item, platform, doc, search, spark, coin, model, shield, thief, trophy,
dice, loop, target, chat, poison) and poster ones (link, trend-up, trend-down, arrow-up, arrow-down, arrow-right, users,
check, cross, alert, bulb, scale, eye, click, chart-bar, chart-line, question, sliders, book, layers, flask, cap, mail, globe,
star, clock, equal). Need another? Add a `<symbol>` to the page's sprite in the same style (48 × 48, stroke = currentColor,
class `ppi`). Inside an SVG chart: `<use href="#spark" x="13" y="33" width="12" height="12" color="#C49A2C"/>`.

## Formulas

MathJax 3 (CommonHTML output, vector in print). Inline `$…$`, display `$$…$$`. Put the paper's macros in the page's
`MathJax.tex.macros` (`bp: "\\boldsymbol{p}"`). Keep `mtextInheritFont: false`: inherited fonts are measured wrongly and leave
gaps under `\underbrace`.

## SVG charts

A chart from the paper: if it was saved by matplotlib as a vector PDF, `tools/figdata.py fig.pdf` prints its lines (x, y),
error bands (lo, hi) and colours as JSON, read from the PDF's drawing operations with the axis mapping from the tick labels
(linear axes, one plot per file). Redraw from that, not from a screenshot.

Use a `viewBox` in millimetres and the same width and height in CSS (`style="width:250mm;height:150mm"`), so a `font-size` of
8.5 is 8.5 mm (24 pt): 7.1 is 20 pt, 8.5 is 24 pt, 10.6 is 30 pt. Give the svg `class="pp-chart"` and `data-fine` (chart
labels may use the fine-print floor), a `role="img"` and an `aria-label` that states what it shows. Subscripts:
`<tspan baseline-shift="sub" font-size="70%">1</tspan>`. Draw from the real numbers; generate long charts with a short script
rather than by hand.

## QR codes

Vector, from LaTeX: `\documentclass{standalone}\usepackage{qrcode}\begin{document}\qrcode[height=4cm,nolink]{URL}\end{document}`,
then `latex` and `dvisvgm --no-fonts --exact-bbox -o img/qr_paper.svg`. A code from an app (a WeChat card) stays a PNG of 300
dpi or more. Check that each one decodes to its URL (in Chrome: `BarcodeDetector`) before printing.

## Builds on screen

`data-build="N"` on any part (an SVG `<g>` or path, a step, a formula box) makes it appear in order of N the first time the
page opens on screen, for a laptop or tablet at the booth and for the review page; ▶ in the controls or the `p` key replays.
Print, the PNG export and `qa` always show the finished poster, and readers who ask for reduced motion see it at once. Use it
for the story parts only (the motivation picture, the model's sequence), at most about fifteen steps.

## Zoom and print

On screen the page fits the window; + and − zoom, 0 fits, 1 shows print size, Ctrl or pinch + scroll zooms at the pointer;
the zoom survives the reload the review page does after each fix. `?export=1` fits the page to the window with no controls
(the PNG), `?view=x,y,w,h` shows a part of it (the close-ups). Printed, `@page` is the page size and nothing else prints.
