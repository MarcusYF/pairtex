---
name: pairposter
description: PairPoster turns a paper (or a LaTeX/Beamer/PDF poster draft) into a conference poster built as one HTML page at its exact printed size, with icons, charts and schematics instead of paragraphs; checks it (overflow, type size at print scale, words per block, phrases not sentences, image resolution, a full view and close-ups); prints the PDF at the venue's size and the PNG for the venue's site; and revises it in a live comment loop in which the author zooms in, drags a box on the poster in a local review page and types. It keeps the author's poster style (how few words, what goes where) in a style guide that learns from their comments and edits, and can start it from their past posters. Use when the author asks for a poster, to polish, shorten or redesign a poster, to turn a paper or Beamer poster into an HTML one, to review, comment on or watch a poster (pairposter, "watch my poster", 海报), or to print or export it. Not for slides, talks or papers.
---

# PairPoster

A poster is an advertisement for a paper, read standing, in passing, from one to two metres. A PairPoster poster is one HTML
page at the venue's size (say 140 × 90 cm): type in points, spacing in millimetres, icons, charts and schematics drawn in SVG,
formulas in MathJax. On screen it fits the window and zooms; printed, it is exactly its size, vector throughout. The engine
(`assets/engine/`) handles the page, the grid of blocks, type, icons, formulas, zoom and print. Your part needs judgement:
finding the one story, choosing what to draw instead of write, cutting words, checking the result, and learning the author's
taste.

PairPoster runs on PairDeck's program (`pairposter` is PairDeck's code in its poster flavour), so the review page, the watcher,
snapshots and style learning work exactly as in PairDeck; posters keep their own data home and style guide.

```
pairposter paths       # where the profile, style vault and posters are
```

Below, `$PP` is the CLI: `pairposter`, or `~/.local/bin/pairposter` when it is not on PATH, or `bin/pairposter` next to this
skill's folder. `$PP <command> -h` lists the options. This skill works in any agent that reads `SKILL.md` files.

| Path (`$PP paths`) | What it is |
| --- | --- |
| `vault/STYLE.md` | The author's poster style, growing. Read it before every poster and when its sha changes |
| visual look | PairDeck's `STYLE.md` (palette, type, icon style), shared with the author's decks; read it too if it exists |
| `vault/preferences.md` | The author's feedback about the loop itself (report language, what to ask first, ...) |
| `vault/evidence.jsonl` | Raw style evidence, one event per line |
| `projects/<slug>/` | Per poster: `project.json` (where it lives), `NOTES.md`, `comments.jsonl`, snapshots, `qa/` screenshots |
| `references/` | `poster.md`, `components.md`, `qa.md`, `learning.md`, `seeding.md` |

No profile yet: ask the author's name and run `$PP setup --name "…" --agent <your name: Claude, Codex, …>`.

## Before every poster

1. **Read `STYLE.md`** in full (its base rules first), the visual-look guide, `preferences.md`, and the poster's `NOTES.md` if
   it exists. Order of authority: the request in front of you; the venue's rules; the base rules; confirmed rules; tentative
   patterns where the case clearly fits; `references/poster.md`; general good practice. Style never changes a claim or a number.
2. **The style guide is empty and the author has past posters?** Offer once to seed it (`references/seeding.md`).
3. **Settle the venue:** the maximum size and orientation (look it up on the venue's poster instructions, or ask), the print
   and upload formats and dates. The page is the venue's maximum size; never larger.

## Build a poster

1. **Read the source in full and write a fact sheet:** the claims and numbers the poster may show, each with its location in
   the paper. An existing poster draft (LaTeX, Beamer, PDF) is a source too: take its facts, logos, links and data (chart
   values, confidence intervals), not its wording. A paper figure made with matplotlib and saved as a vector PDF holds its
   exact data: `python3 <PairPoster>/tools/figdata.py fig.pdf > fig.json` recovers the lines and error bands, so you can
   redraw the chart in the poster's style instead of pasting a picture with small labels.
2. **Find the story** (`references/poster.md`): the one-line takeaway, the question that hooks a passer-by, and four to six
   blocks in reading order. For every block, decide its **picture first**: a chart, a schematic, an icon chain, big numbers,
   a formula worth a glance. Words only label the pictures.
3. **Scaffold:** `$PP new <slug> --title "Main title|Subtitle" --size WxH [--dir DIR]` (size in mm, e.g. `1400x900`). It
   writes `index.html` with the engine in `_poster/` and the icon sprite inlined, and registers the poster. Put images in
   `img/` next to it (copy them in: the review server serves only that folder). Make QR codes vector (`references/components.md`).
4. **Write the poster** with the engine's components (`references/components.md`). Draw charts as inline SVG from the real
   numbers, with viewBox units in millimetres so type sizes are easy to control. Set the venue size and the word budgets in
   `<meta name="pairposter">` from the style guide.
5. **Check it:** `$PP qa <slug>`. It measures the laid-out poster in Chrome (overflow, type below the floor, words per block
   and in all, sentences, image dpi, empty space) and takes the whole poster plus close-ups (`--grid 3x2`). Fix every ERROR.
   Treat warnings as the style guide does. **Open and look at the whole poster and every close-up** (Claude Code: the Read
   tool; Codex: `view_image`) and go through `references/qa.md`. Repeat until clean, then check the facts once more.
6. **Snapshot:** `$PP snapshot <slug> -m "first build"`.
7. **Show it.** Start `$PP review <slug>` in the background and give the author its URL. Say in two lines how to comment:
   zoom with + and − (0 fits, 1 is print size), press **Comment** (or `c`), drag a box, type, Send. Offer to start the loop.

## The comment loop

Start it when the author asks ("watch my poster", or yes to your offer):

1. `$PP status <slug>`. Handle comments still "with the agent" from an earlier session first.
2. Make sure the review page runs (`$PP review <slug>` in the background).
3. Start the watcher **in the background, so that its exit wakes you**: `$PP watch <slug>` (Claude Code: the Bash tool with
   `run_in_background: true`). One watcher per poster; `--takeover` only when the author moves the loop to this session. An
   agent that cannot be woken by a background command polls `$PP watch <slug> --once` every 30 to 60 seconds.
4. Tell the author in one line that you are watching, and where the review page is.

**Changes asked for in chat** (not on the review page), while the loop runs: stop the background watcher first, make the
change, `snapshot`, then watch again. A watcher that sees your edits before the snapshot records them as the author's; if it
happens, `learn --discard <ids> --why "the agent's own edit"`. Until you have snapshotted, run `learn` with `--no-sync`.

**Authorization.** Starting the loop at the author's request authorizes edits to this poster that answer its comments, for
this session. It does not authorize printing services, uploads to a venue, or sending the poster anywhere.

### Each batch

The watcher prints one batch and exits 0 (exit 4: snapshot first; exit 5: another session watches; exit 2: file missing).

1. **Read the batch.** Each comment names its block, the box (fractions of the poster), the words under it, and its thread.
   The author's own edits come as diffs against your last snapshot. Re-read `STYLE.md` if its sha changed.
2. **For each comment:** edit the poster, then `$PP resolve <slug> <id> "<reply>"`. Add `--stated` when a comment states a
   general preference the watcher did not mark.
3. **Check:** `$PP qa <slug>`, and look at the whole poster and the close-ups you touched. A fix in one block often moves the
   others: overflow and empty space are checked across the page.
4. **Snapshot:** `$PP snapshot <slug> -m "c3, c4"`.
5. **Learn** (`references/learning.md`): `$PP learn <slug>`, update `STYLE.md`, `$PP learn --ack <ids>`, commit the vault.
6. **Watch again** and **report** in two to four lines: what changed, any rule learned, anything that needs the author.

### Editing rules

- **Do what the comment asks, at its scope.** The block and the words under the box say what "this" is.
- **Cutting is the default direction.** When a comment says "too much", remove or draw; do not shrink the type below the floor.
- **Never change the facts on your own.** Numbers, claims, conditions of theorems, and author lists change only when a comment
  asks and the source supports it. Dropping a result (a plot, a theorem) is the author's decision: propose it, or do it and
  say so in the reply so the author can undo it.
- **A decision that is the author's** (two layouts, what to cut): reply with the options numbered, and make no edit.
- **Keep the poster working:** the page size never changes; images stay in `img/`; colours come from the tokens.

## Print and deliver

`$PP print <slug>` writes `print/<slug>.pdf` at the page size (one page, vector text, fonts embedded) and
`print/<slug>_<W>x<H>.png` for the venue's site (`--png-width`, `--png-max-height`, `--png-max-mb`; the defaults fit NeurIPS:
at most 5120 × 2880 px and 10 MB). It checks the PDF has exactly one page of the right size. Sending files to a print shop or
uploading them to a venue needs the author's explicit go-ahead.

## Host notes

- **Claude Code.** Run `review` and `watch` with `run_in_background: true`. To look at the poster interactively, open the
  review URL in the browser pane (`preview_start` with the URL).
- **Codex.** Look at screenshots with `view_image`. Invocation: `$pairposter`.

## Stop

When the author says stop, stop the watcher (and the review page unless they still read it), run `$PP learn <slug>` once more,
and say in a few lines what the style guide gained this session.

## Feedback about the loop

Comments on how the loop behaves go to `preferences.md` with the author's words; poster-style feedback goes to `STYLE.md`.

## Files

- `references/poster.md`: what a poster is for, the story, the grammar of blocks, words, type sizes, colour, and turning a
  paper or a LaTeX poster into one.
- `references/components.md`: the page skeleton, blocks and pieces, icons, formulas, SVG charts, QR codes, tokens.
- `references/qa.md`: what `qa` measures, the visual checklist, printing.
- `references/learning.md`, `references/seeding.md`: the style guide's evidence and its seeding.
- `assets/engine/`: `poster.css`, `poster.js`, `icons.svg`, Computer Modern fonts (SIL OFL, `fonts/OFL.txt`) and MathJax 3
  (Apache 2.0, `mathjax/LICENSE`).
- `assets/template.html`: the page `new` starts from.
