# Quality check

Never show the author a deck you have not looked at slide by slide. `pairdeck qa` does the mechanical part; the judgement is
yours.

## Running it

```bash
pairdeck qa <slug>                                    # lint + every slide, light / dark / narrow
pairdeck qa <slug> --slides 3,5-6 --modes light       # a quick re-check
pairdeck qa <slug> --no-shots                         # lint only
pairdeck qa path/to/deck.html                         # a deck that is not registered, or a bundled single file
```

How it works:
- It serves the deck over a temporary local HTTP server. A root-relative engine (`/decks/_deck/`) is found by searching
  upwards; otherwise pass `--root`.
- Each slide is captured after all its build steps, with transitions switched off, so you see the final state, dimmed takeaways
  included.
- **Layout check.** A second headless pass steps through every slide at 1280×800 and reports SVG labels that overlap, spill out
  of their box or past the figure's edge; low-contrast text on boxes (often a fill class that does not exist); arrows that end
  inside a shape; lines drawn through labels; ASCII sub- or superscripts in visible text; headlines that run into the section
  label; content that scrolls inside a box; slides taller than the window or wider than the screen. Treat these as strong hints
  and confirm them on the screenshot.
- **Interaction states.** Screenshots show an interaction's opening state. To capture another:
  `pairdeck qa <slug> --slides 6 --modes light --tag share80 --after 'document.querySelector("#share").value=80;
  document.querySelector("#share").dispatchEvent(new Event("input"))'`.
- **Build order.** `--steps` also captures every intermediate step of the chosen slides (`light-02-step0.png` is before any
  step), so you can check that things appear in a sensible order.
- Screenshots and a contact sheet (`index.html`) go to `projects/<slug>/qa/` in the data home (`--out` to choose). Re-runs
  with `--slides` or `--modes` replace only those PNGs.
- The exit status is 1 if the lint found errors (no engine, a leftover `TODO`, an unknown icon) or a screenshot failed.
- The narrow mode is 520 px wide, the narrowest headless Chrome renders reliably; check a real phone or a phone emulator too
  when one is available.
- It needs Chrome or Chromium; set `CHROME=/path/to/chrome` if it is not found.

## Visual checklist (look at every screenshot)

- **Nothing collides.** No label overlaps a line, an icon or another label. Labels that cross lines have `.knock`. The headline
  stays clear of the section label.
- **Nothing is hidden.** No table or list scrolls inside its box. Split the slide instead.
- **Nothing is clipped:** the top of the first figure, the ends of long labels, text near the viewBox edges. A negative viewBox
  origin (`0 -44 960 424`) is a fine way to make headroom.
- **Text is readable.** SVG text is at least 15 units, and nothing looks small next to the headline.
- **The slide is balanced.** No large empty areas, no crowding. The figure is the hero; the takeaway sits close below it.
- **Colours keep their roles** on every slide, and dark mode keeps its contrast (soft fills and faint text are the usual
  failures).
- **The build order makes sense.** Could the final state have appeared in reading order? Are the dimmed items the ones that
  should recede?
- **Narrow width.** The headline wraps cleanly; wide figures scroll sideways with the key content in the first view; takeaways do
  not overflow.
- **The title slide:** exact title, the rule, a subtitle that poses a question, a correct meta line.
- **The interaction.** Open the deck in a browser if you can and use every control. It must not advance the slide, it must
  redraw correctly, and it must start in a sensible state.
- **The author's guide.** Go through `STYLE.md`'s confirmed rules and its table once against the screenshots: a rule the author
  confirmed must hold on every slide.

## Content checklist

- Compare every number on every slide with the fact sheet, including bar lengths.
- Approximate values carry "≈" and the word "approximate". Illustrations say so.
- Qualifiers survive ("in simulations", "worst case").
- Links work: the back link, the source, the takeaway links.
- No `TODO`, placeholder text, `href="#"` links, real private data, or local absolute paths. The lint flags the first, third
  and last.

## Common fixes

| Symptom | Fix |
|---|---|
| A label collides with a curve | Move the label, add `.knock`, or route the curve around it |
| A table scrolls inside the slide | Split it across slides or turn rows into cards |
| The headline runs into the section label | Shorten it to one line; move detail to the takeaway |
| Empty space under a small figure | Enlarge the figure (`max-width`), or add a meaningful second element |
| A figure is cramped on phones | Keep the essentials in the left two-thirds; shorten labels; split into `.dk-cols` |
| Dark mode looks muddy | Use role classes instead of hex colours; prefer `f-*-soft` fills with a same-hue stroke |
| A wall of text | Turn the sentences into a diagram, keep one takeaway, move details to `.dk-note` |
| A bar length disagrees with its label | Recompute the width from the data with one scale for the whole chart |
| An arrow runs into an icon | End the path a few units before the icon's edge |
