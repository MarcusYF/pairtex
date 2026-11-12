# Learning the author's visual style

The loop collects evidence; you turn it into entries in the vault's `STYLE.md` (`pairdeck paths`). Do this at step 5 of every
batch, after seeding, and once more when the loop stops. The aim is a guide that makes the next first draft need fewer comments,
not a diary of every edit.

## The evidence

`pairdeck learn <slug>` prints each pending event in full (`--all` for every deck and every seed); the batch lists them one line
each. Every event is also in the vault's `evidence.jsonl`, with an id (E0001, ...), a date, a kind and the deck's slug. Kinds,
strongest first:

| Kind | What happened | Where it comes from | What it can teach |
| --- | --- | --- | --- |
| `revised` | The author rewrote part of what you made: a slide, the page's styles, a script | The watcher compares the deck with your last snapshot, slide by slide; `before` is your version, `after` theirs, `diff` the lines | The exact change they made to *your* work: the most direct signal there is |
| `reverted` | The author put back the version from before your last change | The same comparison: the slide now equals your previous snapshot | Something not to do again |
| `stated` | A comment states a preference beyond the slide at hand ("too dense", "never a pie chart", "from now on…") | The watcher marks comments with general words; you add others with `resolve --stated` | A rule in the author's own words |
| `own_edit` | The author's own new work in the deck: a slide they added, a part they had already rewritten | The same comparison | Their habits, when the change is about style rather than content |
| `seed` | One past deck the author gave to `pairdeck seed` | `vault/seed/<id>/` (`references/seeding.md`) | The author's existing taste: palette, type, density, structure |
| `kept` | The author pressed **Keep** on your answer | The review page | Confirms the rules you applied; adds none by itself |

Only the author's own actions count. A comment or an edit by someone else, an edit made by a tool or another session, and your
own output are never the author's style. If an event is not the author's (you edited the deck yourself and forgot `snapshot`,
a test, a colleague's change), do not just acknowledge it: `pairdeck learn --discard <ids> --why "<reason>"` keeps it out of
every later pass with the reason. The watcher refuses to start (exit 4) when you answered comments and changed the deck without
a snapshot, so your edits are not read as the author's.

## From evidence to entries

For each event, ask what general visual move it shows, then do exactly one of these:

1. **Strengthen an existing entry.** Add the event id to its Evidence line (and a short before → after if it is a better
   example).
2. **Add a tentative pattern** (`### Tnn`) when the move is general: how dense a slide is, what a headline does, how a chart is
   labelled, how builds are paced, where caveats go. Write it as an instruction, quote the author's words if any, and give one
   short before → after.
3. **Add a row to the table "Palette, type and layout"** for a concrete visual choice: a colour for a role ("the second
   option: teal, not grey"), a typeface or size, a stroke weight, a layout, a maximum word count. Columns: Aspect, Prefer, Avoid,
   Evidence.
4. **Add to "What … undid"** for a `reverted` event: what you did, what the author restored, why if it is clear.
5. **Deck notes, not the style guide,** for anything specific to one deck: its actors' colour mapping, its terms, its facts.
   Write those in `projects/<slug>/NOTES.md`.
6. **Nothing**, for content changes (a new number, a fixed typo, a reworded fact) and one-off fixes with no pattern. Still
   acknowledge the event.

A `stated` event whose comment is written as a rule ("always", "never", "from now on", "every slide", "以后") goes straight to
**Confirmed rules**, with the author's words. If it turns out to be about the slide at hand only, discard it with the reason.

To read a `revised` diff well, look past the markup: a changed class (`f-soft` → `f-teal-soft`) is a colour choice; a shorter
`.dk-take` is a density choice; a moved `data-step` is a pacing choice; a deleted `.dk-note` may mean "fewer caveats on
slides". Open the deck and the QA screenshot of that slide when the diff alone is unclear.

## Promotion and pruning

- **Tentative → Confirmed** after three independent pieces of evidence (different comments, slides, decks or seeded decks)
  with no counterexample, or at once when the author says it is general. Renumber it `Snn`, keep its evidence.
- **Contradicted** entries: note the counterexample under the entry. Two counterexamples: narrow the entry's scope or delete it.
- **Base rules** change only through the author. When a confirmed rule looks like a top-level principle, ask them in chat
  whether to add it to the base rules; do not edit those yourself.
- Keep the guide short. Merge entries that say the same thing. An entry is at most six lines.
- **Style never changes a fact.** No entry may tell you to round, drop or restate a number, a claim or a result.

## Then

1. Add a dated line to the **Log** at the end of `STYLE.md` naming the events and what changed ("2026-03-02: E0012, E0014 →
   T03 'one takeaway, at most twelve words'; E0013 → What … undid").
2. `pairdeck learn --ack <every id you processed, including those you left alone>` (it works while the watcher runs).
3. Commit the vault (the data home is a git repository unless set up with `--no-git`):
   `git -C <data home> add -A && git -C <data home> commit -m "style: …"`.
4. In the chat report, name any new or promoted rule in one line, so the author can object.

## Using the guide

Read `STYLE.md` before every deck and whenever its sha in the batch header changes. Apply it to every slide you build or rebuild,
and check its confirmed rules and table against the QA screenshots. Do not restyle slides a comment did not touch: a comment
about one slide is not licence to redesign the deck.
