# Checking a talk: every click, with screenshots

Before the author sees a draft, and after every fix, look at what the audience will see. A slide can be right at click 3 and
broken at click 1.

## Every click

```sh
pairtalk shots <talk>                          # every slide, every click, into the talk's shots/ in the data home
pairtalk shots <talk> --ids RESULT1,RESULT2    # only these slides, every click
pairtalk shots <talk> --ids RESULT1 --click 2 --box 700,740,520,110   # one click, with a comment's box drawn on it
```

It uses an installed Chrome (`--chrome PATH` or `CHROME_PATH` if it is not found) and writes one PNG per click, named
`<position>_<slide id>_click-<k>.png`, and `manifest.json`. **`manifest.json` must say `"ok": true`**: it lists console
errors, page errors, failed requests, missing fonts (a maths symbol whose font is not bundled) and images that did not decode,
each with the slide and click.

## Look at them

Open the PNGs of every slide you changed, every click, and check:

- the title fits every click, and nothing overlaps, overflows the frame or wraps where it should not;
- each click adds one thing, and the last click leaves the essentials;
- nothing jumps between clicks (later builds have their space reserved);
- text is large enough (playbook §3.2) and the frame is filled (§3.5);
- every symbol is defined where it first appears; formulas rendered (no raw `\(` or stray `;`);
- the figure's labels sit on what they label;
- the slide matches the comment's request and its box.

For a whole talk, a contact sheet helps: put the PNGs side by side and scan the sequence for empty clicks and uneven margins.

## The script

- `pairtalk script export <talk>` refuses to overwrite a SCRIPT.md that differs from the slides (`--force` does, and loses pending edits); after you change notes in the slide files,
  `pairtalk snapshot <talk>` brings SCRIPT.md up to date and keeps the author's pending edits.
- `pairtalk script apply <talk> --dry-run` should say it would apply 0 notes when SCRIPT.md is in step with the slides.
- Count the words: the script fits the slot at the author's words per minute (STYLE.md, else about 140).

## The speaker view and the bundle

- Open `pairtalk serve <talk>`, press `v`: the speaker window shows the current slide, the next click, the note and the
  timer against `window.DECK_MINUTES`.
- `pairtalk bundle <talk>` writes one offline HTML file (`dist/<talk>.html` in the talk folder) for presenting without a
  network. Open it once before the talk.
