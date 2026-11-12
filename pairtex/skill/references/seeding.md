# Seeding the style guide from the author's own papers

`pairtex seed` turns papers the author already wrote into evidence, so the guide starts close to their voice instead of empty.
Run it when the author asks ("learn my style from these papers", "从我以前的论文学我的风格"), at install time when they offer
papers, or whenever they add more.

## Run it

```
pairtex seed ~/papers/paper-a ~/papers/paper-b.tex ~/papers/paper-c.pdf --note "my three solo papers"
```

- One argument per work: a LaTeX project folder (its main file and everything it `\input`s), a `.tex` file, or a `.pdf`
  (needs `pdftotext`, or macOS). A folder of several projects or PDFs counts each one.
- **Ask for papers the author wrote mostly themselves.** A coauthor's sections are someone else's style. If the author can only
  offer coauthored papers, seed them and treat every entry from them as tentative.
- **Final versions only.** `seed` keeps the newest of several drafts when titles or paragraphs coincide, and skips works under
  `--min-words` (1500), but heavily retitled drafts of one paper still look like separate papers: ask, and pass one version.
- Prefer the `.tex` source over the PDF. PDF text is rough (headers, footnotes, hyphenation) and loses LaTeX habits.

`seed` writes `vault/seed/<seed-id>/` in the data home: `manifest.json` (the works), `stats.json` (per work: sentence and
paragraph length, openings, hedges, connectives, person, passive voice, spelling, punctuation, LaTeX habits such as `\citet`
or `\cref`, macros defined; and `habits`, how many of the works show each common habit), and `samples.md` (the abstract and
the first paragraphs of each section, by section). It adds one `seed` event per work to `evidence.jsonl`. Nothing leaves the
computer.

## Turn it into entries

1. Read `stats.json` (start with `habits`) and all of `samples.md`. Read as an editor: how does this author open a paragraph,
   state a result, hedge, move from one claim to the next, introduce notation, cite, close a section?
2. For each pattern, count the works that show it. A pattern clear in **three or more works** (or in every work when there are
   fewer than three, with at least two) goes into **Confirmed rules** with `Evidence: E0012, E0013, E0015 (seed)`. A pattern in
   one or two works goes into **Tentative patterns**. Numbers from `stats.json` make good evidence lines ("median sentence 18
   words in 5 of 5 papers").
3. Good seed entries are about form, and specific enough to act on:
   - paragraph shape ("Open each paragraph with its claim; the evidence follows").
   - sentence length and rhythm ("Sentences run 15 to 25 words; split anything over 35").
   - voice ("'We' for the authors' actions; never 'this paper shows'").
   - hedging and certainty ("State proven results flat; hedge only empirical claims, with 'suggests'").
   - signposting ("Name the result before the proof: 'Proposition 2 shows that …'").
   - house habits in LaTeX (`\citet` for a subject, `\citep` otherwise; `Figure~\ref`, spelled out; `e.g.,` with a comma;
     American spelling).
   - words to prefer or avoid, in the *Words and phrasing* table, when a choice recurs across works.
4. Never turn content into a rule: topics, results, notation of one paper and coauthors' names stay out. A notation habit that
   recurs across papers (bold vectors, `\mathbb{E}` for expectation) is form and may go in.
5. Keep the guide short: ten to twenty seed entries are plenty. Merge, do not list.
6. Add a line to the **Log** ("2026-11-12: seed-001 (E0012–E0016, five papers) → S01–S06, T01–T09"), run
   `pairtex learn --ack <every seed event id>`, and commit the vault.
7. **Show the author** the five to ten strongest entries in chat, one line each, and say they can delete or edit any entry in
   `STYLE.md`. Their edits win. Base rules stay theirs: suggest one only if a confirmed rule looks like a principle.

## Later

- Feedback from the loop outranks seed evidence: a seed rule the author rewrites against is contradicted like any other entry
  (`references/learning.md`).
- `pairtex seed --list` lists seeds; `pairtex seed --forget <seed-id>` deletes one and discards its events. Then remove the
  entries whose evidence was only that seed.
