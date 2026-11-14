# Making a poster

The author's `STYLE.md` overrides anything here. These are the defaults a first poster follows.

## 1. What a poster is for

A poster is an advertisement for the paper. In a poster session people walk past hundreds of posters; each gets a few
seconds. A poster wins those seconds with one clear picture, a question they care about, and very few words, and then gives
the presenter something to point at while they talk. The paper, one QR code away, holds everything else.

So the measure of a poster is not how much of the paper it contains, but how fast a passer-by can answer three questions:
*what problem? what is new? why should I believe it?* Everything that does not help answer them goes, however true.

## 2. Find the story first

Before any markup, write down:

1. **The takeaway**, in one line of at most about fifteen words. It goes in the footer band, and every block serves it.
2. **The hook**: the question, the surprising fact, or the cost that makes people stop ("Most benchmark gains are memorized").
3. **Four to six blocks in reading order**, usually: why it matters → the setting or model → the main result (theory or
   method) → the evidence → what it means. Number them; columns read top to bottom, left to right.
4. **For every block, its picture**: what a reader sees first. Then the few words that label it.

## 3. Picture first

| Instead of | Draw |
| --- | --- |
| A paragraph of motivation | An icon chain: three to five steps, an icon and three to six words each, arrows between |
| "We consider n agents who…" | A schematic of the setting (the screen, the market, the network) with its actors coloured |
| Theorem statements | The result's shape as a picture (bars that are flat within a group, a region, a phase diagram), the formula worth a glance, and a one-line claim with a tag ("Thm 4.1") |
| A table of numbers | A chart with direct labels; the two or three numbers that matter set large (`.pp-stats`) |
| A list of findings | Icon rows: a check, a cross, a star, a trend arrow, each with a phrase |
| Implications | Two or three cards: an icon, a key phrase, three to six words |

Charts: draw them from the real numbers (the paper's tables, the draft poster's data), with error bars when the paper reports
them, direct labels instead of legends where possible, and one colour per series used consistently across the poster.
Figures from the paper may be reused as images (200 dpi or more at their printed size), but their small labels often fall
below the floor; redraw the one that carries the result when the data is available, and say when it is not.

## 4. Words

- **Phrases, not sentences.** "labels cost 10× less", not "This approach reduces the cost of collecting labels by an order
  of magnitude." No full stops in bullets.
- **Budgets** (defaults, unless the style guide sets others): about 250 words on a 140 × 90 cm or A0 poster, not counting the
  title band, formulas, chart labels and fine print; about 45 per block; a block heading of at most six words that states the
  point ("Cheaper labels, same accuracy"), not the topic ("Theoretical results").
- **Symbols do work words would do**: ↑ ↓ → · ≥ "0.71 → 0.84".
- **Keep the claim exact.** Shortening never drops a qualifier that changes the claim ("in every tested setting", "vs. no
  mechanism"). Keep theorem conditions as a small formula ("$\beta\ge 2$") or in the tag.

## 5. Type and layout

- **Sizes for a 140 × 90 cm or A0 poster:** title 80–90 pt, block headings 40–46 pt, body 32–36 pt, secondary 28–30 pt; no
  text under 24 pt, fine print (captions, chart ticks, affiliations, tags) not under 20 pt. Scale with the page: an A1 poster
  takes about 70% of these.
- **One typeface** (the author's, from the visual-look guide), bold for headings and key phrases, the accent colour for
  structure, a second colour only for meaning (good/bad, a series).
- **Columns:** three for landscape, two or three for portrait. Blocks fill their column (`.pp-grow`); spare height is spread
  inside a block (`.pp-spread`), not left at the bottom of one.
- **Title band:** the title (two lines at most: main title and subtitle), authors, affiliations, venue; logos and the paper's
  QR code on the right.
- **Footer band:** the takeaway, and the presenter's card (name, what they are looking for, QR codes to their page) when the
  poster should also advertise the person.
- **White space is not waste**, but a block that ends half empty means its picture should be larger.

## 6. Colour

The accent family (from the visual-look guide, or the institution's colour if the author asks) carries structure: headings,
numbers, the takeaway band. One colour per actor or series, the same everywhere: if the platform is gold in the schematic, it
is gold in the icons and the list. Colour never carries meaning alone: pair it with a label, a marker or an icon.

## 7. From a LaTeX or Beamer poster

1. Copy logos, figures and the QR targets into `img/`; crop logos to their visible edge (`trim` values in the LaTeX are the
   crop). Make QR codes vector: `\qrcode{URL}` in a standalone LaTeX file, `latex`, then `dvisvgm --no-fonts --exact-bbox`.
2. Take chart data from `pgfplots` coordinates and TikZ drawings, not by reading the PDF.
3. Map each LaTeX box to a block, then cut: most boxes become a picture plus three to five phrases.
4. Keep the author list, affiliations, venue line and links exact.
5. Leave the LaTeX source and its PDF untouched; the HTML poster lives next to them (for example in `web/`).

## 8. What to avoid

Paragraphs. Sentences in bullets. A legend where a direct label fits. Logos larger than the title. Three plots where one
makes the point. Type shrunk to make text fit (cut instead). Decorative gradients and drop shadows. Any number that is not in
the fact sheet.
