# Checking a poster

## What `pairposter qa` measures

It loads the poster in headless Chrome, waits for the fonts and every formula, and reports:

| Line | Meaning | What to do |
| --- | --- | --- |
| `ERROR overflow: [Block] … N mm too tall` | Content spills out of its box (clipped in print) | Cut words, shrink the picture, or move a part; never shrink type below the floor |
| `ERROR type X pt < floor` | Text under `min_pt` (or under `fine_pt` in fine print and charts with `data-fine`) | Enlarge it, or cut it; superscripts and subscripts are not counted |
| `ERROR N TODO left` | Placeholders from the template | Fill or delete |
| `ERROR image not loaded` | A broken `src` | Copy the image into `img/` |
| `warning words: …` | A block, or the poster, over its word budget | Cut, or draw |
| `warning a sentence / long` | A text of 7+ words ending in a full stop, or of 13+ words | Make it a phrase |
| `warning image … dpi` | An image under 150 dpi at its printed size | Use a larger file or redraw |
| `note N mm empty` | Spare height at the bottom of a block or column | Enlarge its picture, or `.pp-spread` |

Words are counted outside the title band, formulas, SVG drawings, fine print and QR labels.

## Look at it

`qa` writes `poster.png` (the whole poster) and close-ups `close-r1c1.png`… (default 3 × 2, each a sixth of the poster at
readable size) into the project's `qa/` folder. Open the whole poster first, then every close-up.

**The whole poster, at a glance:**
- Where does the eye land first? It should be the title, then the hook, then the main picture.
- Is there one picture that carries the story? Could a passer-by say what the poster is about in five seconds?
- Are the columns balanced, the blocks aligned, the spacing even? No block half empty, no block crammed.
- Is colour used for meaning only, the same way everywhere?

**Each close-up:**
- No text overlaps a mark, another label or a block edge; no label is clipped.
- Formulas set correctly (no gaps inside braces, no raw `$…$`).
- Chart labels are readable; series are told apart by more than colour.
- Phrases, not sentences; numbers match the fact sheet; theorem tags and conditions are right.

Then check the facts once more against the paper.

## Print

`pairposter print <slug>` writes the PDF and the PNG into `print/` next to the poster and checks the PDF has exactly one page
of the poster's size. Two pages mean something spills below the page: run `qa` and fix the overflow. Open the PNG to see what
the venue's site will show. Before sending a file to a print shop, open the PDF at 100% in a viewer and look at a corner: text
must be sharp (vector), images at least 150 dpi.
