# Learning the author's poster style

The loop collects evidence; you turn it into entries in the vault's `STYLE.md` (`pairposter paths`). Do this at step 5 of
every batch, after seeding, and once more when the loop stops. The aim is a guide that makes the next first draft need fewer
comments, not a diary of every edit.

## The evidence

`pairposter learn <slug>` prints each pending event in full (`--all` for every poster and every seed). Kinds, strongest first:

| Kind | What happened | What it can teach |
| --- | --- | --- |
| `revised` | The author rewrote part of what you made (a block, the page's styles); `before` is your version, `after` theirs | The exact change they made to your work: the most direct signal |
| `reverted` | The author put back the version from before your last change | Something not to do again |
| `stated` | A comment states a preference beyond the block at hand ("too many words", "never a legend", "以后…") | A rule in the author's own words |
| `own_edit` | The author's own new work on the poster | Their habits, when the change is about style rather than content |
| `seed` | One past poster given to `pairposter seed` | Their existing taste: palette, type, density, layout |
| `kept` | The author pressed **Keep** on your answer | Confirms the rules you applied |

Only the author's own actions count. A coauthor's comment, an edit made by a tool or another session, and your own output are
never the author's style: `pairposter learn --discard <ids> --why "<reason>"`. The watcher refuses to start (exit 4) when you
answered comments and changed the poster without a snapshot, so your edits are not read as the author's.

## From evidence to entries

For each event, ask what general poster move it shows, then do one of these:

1. **Strengthen an existing entry**: add the event id to its Evidence line.
2. **Add a tentative pattern** (`### Tnn`) for a general move: how many words a block takes, what a heading does, how results
   are shown, how much a figure from the paper is trusted, what the title band holds. Write it as an instruction, quote the
   author's words, give one short before → after.
3. **Add a row to the table** for a concrete choice: a word budget, a type size, the number of columns, a colour for a role.
4. **Add to "What … undid"** for a `reverted` event.
5. **Poster notes, not the style guide,** for anything specific to one poster (its colours per actor, its terms, its facts):
   `projects/<slug>/NOTES.md`.
6. **Nothing**, for content changes and one-off fixes. Still acknowledge the event.

A `stated` event written as a rule ("always", "never", "from now on", "every poster", "以后") goes straight to **Confirmed
rules**, with the author's words. Base rules change only through the author; when a confirmed rule looks that general, ask.

When the author's comments show a different taste for the numbers (a word budget, a type size), update the poster's
`<meta name="pairposter">` budgets and the table row together.

## Promotion and pruning

- **Tentative → Confirmed** after three independent pieces of evidence (different comments, blocks, posters or seeds) with no
  counterexample, or at once when the author says it is general. Renumber it `Snn`.
- Two counterexamples: narrow the entry or delete it. Merge entries that say the same thing; an entry is at most six lines.
- **Style never changes a fact.**

## Then

1. Add a dated line to the **Log** at the end of `STYLE.md` naming the events and what changed.
2. `pairposter learn --ack <every id you processed>`.
3. Commit the vault: `git -C <data home> add -A && git -C <data home> commit -m "style: …"`.
4. In the chat report, name any new or promoted rule in one line, so the author can object.
