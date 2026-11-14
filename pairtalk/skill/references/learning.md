# Learning the author's talk style

The loop collects evidence; the agent turns it into rules in the vault's `STYLE.md` (`pairtalk paths`). Do this at step 7 of
every batch, and once more when the loop stops. The aim is a guide that makes the next first draft need fewer comments, not a
diary of every edit. The contract all PairLab tools share is `docs/style-vault.md` in the repository.

## The evidence

`pairtalk learn <talk>` prints each pending event in full; the batch shows one line each; `pairtalk learn --all` adds the
seeds. Every event is in the vault's `evidence.jsonl` with an id (E0001, ...). Kinds, strongest first:

| Kind | What happened | What it can teach |
| --- | --- | --- |
| `revised` | The owner rewrote what you made: a note (in SCRIPT.md, in the browser's script panel, or in the slide file) or a slide file. `before` is your version, `after` theirs | The exact change they made to your work: the most direct signal |
| `reverted` | The owner restored what you had replaced | Something not to do again |
| `stated` | The owner's comment states a preference beyond the slide at hand: the watcher records comments with "always", "never", "every time", "以后", …; you add others with `resolve --stated` | A rule in their words |
| `own_edit` | The owner changed text they or a template wrote, not yours (a template placeholder, their own note, a coauthor's wording) | Their habits, when the change is about style rather than content |
| `seed` | One past talk the owner gave to `seed`: its stats and samples | Their baseline: pace, words per slide, how they open and close |

Only the owner's own comments and edits are evidence. The batch marks every comment and edit as the owner's (the profile's
name; on the review server on the owner's computer, also an unnamed comment) or a coauthor's; a coauthor's never becomes
evidence, even when it says "always". If an event still is not the owner's (a coauthor typed the owner's name, an edit was
yours but no snapshot recorded it): `pairtalk learn --discard <ids> --why "<reason>"`.

## From evidence to entries

For each event, ask what general move it shows, then do exactly one of these:

1. **Strengthen an existing entry.** Add the event id to its Evidence line.
2. **Add a tentative pattern** (`### Tnn`) when the move is general: how a slide is titled, what stays off the slide, how a
   build is paced, how a note opens or hands over to the next slide. Write it as an instruction, quote the author's words if
   any, and give one short before → after.
3. **Add a row to the Pacing and script table** for the script's measurable habits: words per minute, words per click, how a
   talk opens, how a slide hands over, how a talk closes, voice.
4. **Add to What … undid** for a reverted change: what you did, what the author restored, why if it is clear.
5. **Talk notes, not the style guide,** for anything specific to one talk: its terms, its numbers, the venue's framing. Write
   those in `projects/<talk>/NOTES.md`.
6. **Nothing,** for content changes (a new number, a fixed fact, a moved figure) and single-word fixes with no pattern. Still
   acknowledge the event.

Visual habits (palette, type, layout) belong to PairDeck's style guide when the author uses PairDeck; record them there only
if the author asks, and otherwise as a tentative pattern here.

## Promotion and pruning

- **Tentative → Confirmed** after three independent pieces of evidence (different comments, slides or talks) with no
  counterexample, or when the author says it is general. Renumber it `Snn`, keep its evidence.
- **Contradicted** entries: note the counterexample under the entry. Two counterexamples: narrow it or delete it.
- **Base rules** change only through the author. When a confirmed rule looks like a top-level principle, ask them in chat.
- Keep the guide short. Merge entries that say the same thing. An entry is at most six lines.

## Then

1. Add a dated line to the **Log** at the end of `STYLE.md` naming the events and what changed
   ("2026-11-12: E0012, E0014 → T03 'one formula per line'; E0013 → What … undid").
2. `pairtalk learn --ack <every id you processed, including the ones you skipped>` (it works while the watcher runs).
3. Commit the vault: `git -C <data home> add -A vault && git -C <data home> commit -m "talk style: …"`.
4. In the chat report, name any new or promoted rule in one line, so the author can object.

## Using the guide

Read `STYLE.md` at the start of the loop and whenever its sha in the batch header changes. Apply it to every slide and note
you write or rewrite for a comment. Do not restyle slides a comment did not touch.
