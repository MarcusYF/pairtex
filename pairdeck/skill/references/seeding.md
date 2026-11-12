# Seeding the style guide from the author's past decks

A new style guide is empty, so the first deck follows PairDeck's defaults. Seeding reads decks the author already made and
turns them into evidence, so the first draft is already close to their taste.

## Run it

```bash
pairdeck seed ~/talks/2025-workshop.pptx ~/exports/ --note "my last three conference decks"
pairdeck seed --list                 # past seeds, their files and events
pairdeck seed --forget seed-002      # remove a seed's folder and discard its events
```

- **Accepts** files and folders (searched recursively): `.pptx`, `.pdf` exports of slides, `.html` decks. A `.key` file is
  listed as skipped: ask the author to export it from Keynote to PDF or PPTX first.
- **Ask which decks are the author's own**, made mostly by them and recent enough to reflect their taste. Leave out decks built
  on someone else's template, a conference's mandatory theme, or a coauthor's design.
- It runs `shared/seed_visual.py` on the author's computer, writes only into `vault/seed/<seed-id>/` in the data home, never
  changes or uploads the inputs, and adds one `seed` event per file.

## What you get

| File | What is in it |
| --- | --- |
| `samples.md` | Per file: palette, fonts, words per slide, page images; then per slide its layout, title, text and speaker notes |
| `stats.json` | Over all files: `palette` (colours with their share and a role hint: accent, light or dark neutral), `fonts`, `font_sizes`, `words_per_slide`, `titles`, `title_words`, `notes_words_per_slide`, `layouts`, `builds_per_slide` (HTML); `per_file` summaries, PPTX theme colours and fonts, HTML custom properties |
| `pages/<stem>-NN.png` | Up to 12 evenly sampled pages per PDF (and per PPTX when LibreOffice can export it) |
| `manifest.json` | Each file's path, SHA-256, format, page count and images; skipped files with the reason |

Palette shares are per file and then averaged, so a long deck does not outweigh a short one. For PDFs they come from the
pixels of the sampled pages; for PPTX from the theme and the colours the slides use; for HTML from the CSS and how often each
colour or custom property is used.

## Then draft entries

1. **Look**, in this order: the page images (open them: Claude Code's Read tool, Codex's `view_image`), `stats.json`,
   `samples.md`. Note what recurs across decks: background and text colours, one or two accents and what they mark, typefaces for
   titles and body, title length and form (a claim or a topic), words per slide, how much is picture versus text, chart style,
   how slides open and close, how builds are paced (HTML).
2. **Draft entries in `STYLE.md`** (`references/learning.md` for the forms):
   - each seeded file is one independent piece of evidence;
   - a pattern clear in **three or more** seeded files may enter as a confirmed rule, its evidence line saying `(seed)` and
     naming the event ids; fewer goes in as tentative;
   - concrete choices go in the table "Palette, type and layout" (a colour by hex and role, a typeface, a size range, a word
     budget);
   - **content never becomes a rule**: topics, results, names, logos and institution templates are not the author's style.
3. **Map colours to roles.** If the author's decks use, say, a navy and an orange, write which role each plays (system,
   producers) in a table row, so the engine's role classes can follow them: the agent sets the deck's tokens in `deck.css` once.
4. **Show the author, in chat,** the five to ten strongest entries, each in one line with how many decks support it, and ask
   them to delete or change any. Their edits win.
5. `pairdeck learn --ack <the seed event ids>`, add a Log line ("2026-03-02: seed-001 (E0001–E0004) → S01–S03, T01–T04, four
   table rows"), and commit the vault.

## Later

A seed can be forgotten at any time (`seed --forget`); then remove the entries whose only evidence was that seed. Seeding again
later (new decks) adds evidence; it does not replace what the loop learned from comments and edits, which ranks higher because
it is about the decks PairDeck makes.
