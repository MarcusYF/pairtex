# Changelog

## 0.1.0 (unreleased)

The first version, as PairLab's fourth tool.
- **Posters at print size.** `pairposter new <slug> --size WxH` scaffolds one HTML page at the venue's size (mm), with the
  poster engine (`skill/assets/engine/`): a grid of blocks, icon chains, cards, big numbers, formula boxes (MathJax 3), icon
  rows, takeaway band and QR cards, type in points, 45 line icons inlined, Computer Modern fonts. On screen the page fits the
  window and zooms (+, −, 0, 1, Ctrl or pinch + scroll); the zoom survives reloads; printed, it is exactly its size.
- **Checks.** `pairposter qa` measures the laid-out poster in headless Chrome after fonts and formulas are ready: overflow per
  block, type under `min_pt` (fine print under `fine_pt`; SVG text at its drawn scale; indices not counted), words per block
  and in all against the budgets in `<meta name="pairposter">`, sentences, image dpi at print size, empty space; plus a
  picture of the whole poster and close-ups (`--grid 3x2`).
- **Print.** `pairposter print` writes a one-page vector PDF at the page size (checked) and the PNG for a venue's site
  (`--png-width`, `--png-max-height`, `--png-max-mb`; defaults fit NeurIPS).
- **The comment loop** is PairDeck's (review page, watch, resolve, snapshot, learn, seed), in its poster mode: comments name
  the block under the box, boxes stay on their content at any zoom, batches speak of the poster.
- **A poster style vault** (`~/.pairposter`), with its own template; the visual look is read from PairDeck's guide.
- **The skill** (`skill/SKILL.md`, `references/poster.md`, `components.md`, `qa.md`, `learning.md`, `seeding.md`): what a poster is
  for, picture-first grammar, word budgets, type sizes for print, turning a LaTeX or Beamer poster into one.
- `tests/test_e2e.py`: 31 checks (the measured checks, screenshots and printing need Chrome).
