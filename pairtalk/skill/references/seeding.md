# Seeding the talk style from past talks

`pairtalk seed` lets the first draft start close to the author: it reads talks they already gave and stores what it finds in
the vault, and you turn that into STYLE.md entries. It follows the shared contract (`docs/style-vault.md`, §4).

## Run it

```sh
pairtalk seed ~/talks/seminar.pptx --duration 45 --note "department seminar, given alone"
pairtalk seed ~/talks/conference.pdf ~/talks/conference-script.md --duration 15 --note "conference talk"
pairtalk seed ~/talks/old-pairtalk-folder --duration 20
```

- **Slides:** `.pptx` (with its speaker notes), `.pdf` exports, PairTalk talk folders (with their notes), `.html` decks.
  Keynote: export to PDF or PPTX first. A folder of files is searched for `.pptx`, `.pdf` and `SCRIPT.md`.
- **Scripts:** `SCRIPT.md`, or any `.md` or `.txt` script (split at its headings, one part per slide).
- **`--duration`** is each talk's length in minutes and gives words per minute. Give one talk per call when lengths differ.
- Prefer talks the author made and gave alone: a coauthor's slides teach their style, not the author's.

It writes `vault/seed/<seed-id>/`: from the visual extractor (the suite's `shared/seed_visual.py`) `manifest.json`,
`stats.json`, `samples.md` and `pages/*.png`; from PairTalk `script.json` (per talk: slides, words, words per slide, words per
minute, how it opens and closes, sample notes), a `talk` section in `stats.json` and a *Speaker scripts* section in
`samples.md`; and one `seed` event per file in `evidence.jsonl`. `pairtalk seed --list` lists seeds; `pairtalk seed --forget
<seed-id>` deletes one with its events (remove what it added to STYLE.md by hand).

## Turn it into entries

1. Read `samples.md`, `stats.json`, `script.json` and a few page images per talk (`pairtalk learn --all` lists the events).
2. Fill the **Pacing and script** table: words per minute, words per slide and per click, how talks open, how slides hand
   over, how talks close, voice (person, tense, register). Quote short phrases from the samples as evidence, marked `(seed)`.
3. Look for slide habits across the page images: how titles are phrased, how many words a slide holds, what is in boxes,
   how figures are labelled, how many clicks a slide has.
4. **Three or more seeded talks showing the same pattern** may enter as a confirmed rule, its evidence line saying `(seed)`;
   fewer goes in as a tentative pattern. Each seeded file is one independent piece of evidence.
5. **Content never becomes a rule:** topics, results, names and numbers stay out. Only how the talk is built and spoken.
6. Visual habits go to PairDeck's guide if the author uses PairDeck; ask before writing there.
7. Show the author, in chat, the five to ten strongest entries; they may delete or edit any. Then
   `pairtalk learn --ack <the seed events>`, add a Log line, and commit the vault.
