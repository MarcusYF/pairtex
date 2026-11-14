# Seeding the style guide from the author's past posters

A new style guide is empty, so the first poster follows PairPoster's defaults (`poster.md`). Seeding reads posters the author
already made and turns them into evidence, so the first draft is already closer to their taste.

```bash
pairposter seed ~/posters/icml-2025.pdf ~/posters/ --note "my last three conference posters"
pairposter seed --list                 # past seeds, their files and events
pairposter seed --forget seed-002      # remove a seed's folder and discard its events
```

- **Accepts** files and folders: `.pdf` (the usual format of a poster), `.pptx`, `.html`. It runs `shared/seed_visual.py`
  on the author's computer, writes only into `vault/seed/<seed-id>/`, and adds one `seed` event per file.
- **Ask which posters are the author's own** and recent. Leave out posters made by a coauthor or on a lab template the author
  did not choose.

## Turn a seed into entries

1. Read `vault/seed/<id>/samples.md`, `stats.json` and the page images in `pages/`.
2. Note what recurs across posters: the palette and what each colour marks, the typeface, the number of columns, the title
   band, how results are shown (charts, big numbers, tables), how many words a block takes, what is in the footer.
3. Write tentative patterns (`### Tnn`) and table rows, with the seed's event ids as evidence. A pattern seen in three or
   more seeded posters becomes a confirmed rule.
4. **The author's stated principles outrank the seed.** A past poster dense with text does not override "fewer words":
   record the density as a fact about the past, not a rule.
5. Show the author, in chat, the five to ten strongest entries, each in one line with how many posters support it; then
   `pairposter learn --ack <ids>` and commit the vault.

The visual look (palette, typeface, icon style) is shared with PairDeck: if the author's decks were seeded there, read that
guide rather than repeating it here.
