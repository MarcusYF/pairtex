# Visual language: PairDeck's defaults

These are the defaults. The author's `STYLE.md` (in the vault, `pairdeck paths`) ranks above them: where the two disagree,
follow `STYLE.md`. The tokens live in `assets/engine/deck.css`; use its classes rather than hard-coded colours, so dark mode
keeps working.

## Contents
1. Canvas and type
2. Colour roles
3. Icons
4. Diagram craft
5. Charts
6. Motion and builds
7. Slide patterns
8. Words
9. What to avoid

## 1. Canvas and type

- White canvas, with dark mode handled by the engine through `prefers-color-scheme`. The deck sits between a thin top bar (back
  link, title, source link) and a bottom bar (arrows, dots, slide counter).
- One serif family, Computer Modern (CMU Serif, bundled), for slides and SVG text. A sans family appears only in the chrome (top
  and bottom bars, hints). When the author's guide names other typefaces, set them in `deck.css` once, not per slide.
- Headlines are centred and normal weight (`h1.dk-h` on the title slide, `h2.dk-h` elsewhere), and fit on one line (about 60
  characters). The title slide has a gold rule (`hr.dk-rule`), a subtitle (`.dk-sub`) that poses the question in plain words,
  and a meta line (`.dk-meta`: authors · occasion and year).
- Every slide except the title gets a small grey section label: `data-label="Setting"`, "Problem", "Result 1", "Evidence",
  "Try it", "Takeaways".
- Below the picture come one takeaway line (`.dk-take`, ink colour, larger), then an optional muted note (`.dk-note`) for
  caveats, sources or "schematic" labels.

## 2. Colour roles

Colour carries meaning, and the meaning stays the same on every slide and in every deck, so a reader who has seen one deck
reads the next one faster.

| Role | Token / classes | Typical actors |
|---|---|---|
| People | `--people` blue · `c-people f-people s-people t-people` | users, consumers, learners, patients, voters |
| Producers | `--creator` orange · `c-creator …` | creators, sellers, workers, data contributors, inputs |
| System | `--platform` purple · `c-platform …` | platform, mechanism, algorithm, model, designer |
| Good | `--good` green | welfare, totals, "works", correct |
| Bad | `--bad` red | harm, loss, failure, attacks, errors |
| Emphasis | `--gold` | numbering, highlights, the title-slide rule |
| Alternative | `--teal` | the comparison option, a second policy, a rival |
| Neutral | `ink`, `muted`, `faint`, `line`, `soft` | axes, captions, scaffolding |

Each colour has a soft fill (`f-people-soft`, `f-creator-soft`, `f-platform-soft`, `f-good-soft`, `f-bad-soft`,
`f-teal-soft`, `f-soft`). Pair a soft fill with the stroke of the same hue. Use only classes the engine defines: a class that
does not exist falls back to black (`qa` flags low-contrast text on boxes). Map the material's actors to the roles in the
storyboard, keep the mapping for the whole deck, write it in the deck's `NOTES.md`, and add a small legend when it is not obvious:

- **Course concept:** the people affected are blue, the model or estimator purple, data and inputs orange.
- **Tool or project:** the user is blue; the user's content (documents, slides, data) orange; the tool's own logic purple;
  off-the-shelf parts it relies on neutral grey; an optional external service teal, dashed when optional.
- **Proposal:** the people helped are blue, the proposed method purple, aims or milestones gold-numbered.
- **Two compared groups or options** that are neither good nor bad (group A and group B, two treatments, two cohorts): blue and
  teal, with `f-people-soft` and `f-teal-soft`. Keep green and red for good and bad outcomes. A third, neutral class (a
  baseline) is grey with `f-soft`.
- When the source uses other colours, keep the house roles and show the mapping in a legend.

## 3. Icons

- Use the sprite in `assets/engine/icons.svg`: 48×48 line icons, stroke 2.6, round caps, `currentColor`. Available: `person`,
  `robot`, `creator`, `item`, `platform`, `doc`, `search`, `spark`, `coin`, `model`, `shield`, `thief`, `trophy`, `dice`,
  `loop`, `target`, `chat`, `poison`.
- Colour an icon with a role class on the nested `<svg class="icon c-people">`.
- When an icon is missing, draw it inline in the same language: 48 grid, the same stroke weight, round joins, no fills except
  small solid dots. Never mix in filled clip art or emoji.
- Repeat an icon to show many (three creators, six users) rather than writing "many".

## 4. Diagram craft

The bar: solid and considered, rich in detail without clutter, never cheap.

- **ViewBox.** Most figures are 860 to 960 units wide. Text is at least 15 units (labels 17 to 24, captions 15) so it stays
  readable when the SVG scales down.
- **Phones.** Below a width of 640, a figure wider than 520 units keeps 70% of its width and scrolls sideways. Use one wide
  figure only where its left part makes sense alone (a left-to-right flow whose start is the point). When the result sits on
  the right (bars, scores, a verdict), split the picture into two figures of at most 520 units inside `.dk-cols`
  (equal) or `.dk-cols--2-1` / `.dk-cols--1-2`; they sit side by side on desktop and stack on phones.
- **Strokes.** `.ln` (2) for connections, `.ln-thin` (1.2) for axes and guides, `.ln-thick` (3) for the one path that matters.
  `.dash` for "would be", "reference", "optional" or "best possible"; a dashed path with `.dk-draw` fades in.
- **Shapes.** Rounded rectangles (rx 4 to 6) with a soft fill and a same-hue stroke of 1.6 to 1.8. Align shapes to a visible
  grid and space repeated items evenly.
- **Flow.** Lay actors out left to right with curved connectors (`C` paths) that draw in. **Arrows stop at the edge of the shape
  or icon they point to, with a small gap**; they never run into it (`qa` flags arrow ends inside shapes).
- **Labels.** Put a label close to what it names. **A line never runs through a label**: place labels in empty space next to a
  line's end, or give them the `.knock` halo (`qa` flags it).
- **Direct labels** instead of legends whenever possible: colour the label with the role colour (`t-good`) next to its bar or
  line.
- **Detail that helps recognition:** small concrete cues (a die for chance, a magnifier for search, three small cards for a
  top-3 list), nothing ornamental.
- One focal point per figure; mute the scaffolding with `faint` or `muted`.
- **Maths.** When a formula is needed, typeset it (native MathML, or MathJax rendered to SVG ahead of time), never as ASCII
  (`x_t`, `^k`) or Unicode subscript hacks. Inside SVG figures keep symbols plain, with real `<tspan>` sub- and superscripts.

## 5. Charts

- Prefer horizontal bars with the category label on the left (`text-anchor="end"`) and the value just past the bar's end,
  coloured by role. A dashed reference line marks "best possible" or "baseline" when it helps.
- Put the axis meaning as one muted line above the chart ("success rate, %"), and the source as one faint line below.
- **Bar lengths come from the data with one scale for the whole chart**: a bar at 56% is visibly 56% of its reference.
- Bars grow in with `.dk-grow`, staggered by `transition-delay` in steps of 0.08 s. Numbers can count up with `data-count-to`.
- Lines over time draw in with `.dk-draw`. Mark invented curves "schematic".
- A value read off a published figure shows "≈" and the note says "approximate".
- **Results over several runs** show the mean with ± 1 standard deviation (a band on curves, whiskers on bars), and the legend
  says how many runs or seeds. A series with one run says "1 run". A prediction drawn on the same axes is its own mark (a
  dashed line or a hollow ring), so the eye compares the two.
- **Every parameter that sets a regime is in the panel's label**, not only the one the story is about ("α = 0.2, β = 9.6"). When
  a knob's effect depends on what is held fixed, show both comparisons side by side and name the fixed quantity in each title.

## 6. Motion and builds

- **Order.** Steps follow reading order: actors appear, then arrows draw, then results grow, then the takeaway lands. Use 2 to 5
  steps per slide.
- **Dimming.** When a slide has several takeaways, dim the earlier ones as the next appears: `data-step="1" data-dim="2"`.
- **Entrances.** `.dk-rise` (a small upward entrance) for text and groups; `.dk-pop` for one emphasised mark.
- **Continuous motion.** `.dk-flow` (marching dashes) and `.dk-pulse` only for something genuinely ongoing. At most one per
  slide.
- The engine respects reduced-motion settings, and so must custom scripts: check
  `matchMedia('(prefers-reduced-motion: reduce)')` before animating.

## 7. Slide patterns

`components.md` has snippets for each.

- **Title.** Exact title, gold rule, a question as the subtitle, the meta line, and the hint "Press → or click to step through".
- **Actors and flow.** The setting: who does what, built in 3 to 5 steps.
- **Contrast.** Two columns (`.dk-cols`): the good case and the bad case, or option A and option B, each revealed in turn.
- **Result chart.** Growing bars with direct labels, and takeaways that dim in sequence.
- **Schematic over time.** Drawn curves, a highlighted band, and the note "Schematic, not data".
- **Worked example.** After an abstract result, a case small enough to check by hand: a table of the inputs, two cases side by
  side that differ only in the mechanism the result names, and the numbers each gives.
- **Try it.** A real interaction: buttons with `aria-pressed`, or a slider inside `[data-interactive]`, redrawing a chart from
  the source's numbers or a clearly labelled schematic.
- **Takeaways.** `ol.dk-list` with three gold-numbered items, each a short title plus one sentence, then the links.

## 8. Words

- **Headlines state the point.** "Within each group, A does better", not "Results".
- **Few words.** Sentences are short, warm and concrete, for a smart reader from another field. Aim well under 40 words of running
  text per slide; a deck someone presents live needs fewer still.
- **Define every term and symbol** the first time it appears, or replace it with a picture. A symbol that is never defined
  does not go on a slide.
- **One takeaway per slide.** Caveats go in the note, not in the takeaway.
- **No formulas by default.** If the audience needs one, one native MathML expression, in a note or set large with each part
  labelled in words.
- **Fractions** as "1/4" or MathML: the bundled CMU font lacks the ¼ ½ ¾ glyphs.

## 9. What to avoid

- Walls of text, bullet lists in place of pictures, a table that scrolls inside its box (split it across slides or turn rows
  into cards; screenshots and PDFs cut what scrolls).
- Tiny SVG text, labels far from their marks, legends that force eye travel.
- Decorative gradients, drop shadows, emoji, stock images, a third typeface.
- Hard-coded colours that break dark mode.
- Unlabelled illustrations that could be mistaken for data.
- Animations that delay reading: no long sequences and no motion without meaning.
- Typed cross-references such as "see slide 7": slides move. Refer to the section label, or build the reference from it.
