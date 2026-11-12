# Learning the author's writing style

The loop collects evidence; the agent turns it into rules in the vault's `STYLE.md` (`pairtex paths`). Do this at step 4 of every batch, and once more
when the loop stops. The aim is a guide that makes the next first draft need fewer comments, not a diary of every edit.

## The evidence

`pairtex learn <slug>` prints each pending event in full; the batch shows one line each. Every event is also in the vault's `evidence.jsonl`
with an id (E0001, E0002, ...). Kinds, strongest first:

| Kind | What happened | What it can teach |
| --- | --- | --- |
| `closed` with `revised` | The author accepted the thread after rewriting your text | The exact change they made to *your* prose: the most direct signal there is |
| `revised` | The author rewrote text you wrote (thread may still be open) | Same |
| `closed` with `reverted` or `removed` | The author undid your edit | Something not to do again |
| the comment text itself | What the author asked for, in their words | Stated preferences ("too dry", "jargon", "以后都...") |
| `own_edit`, `own_addition`, `own_deletion` | The author's own writing in their editor | Their habits, when the change is about style rather than content |
| `closed` with `kept` | The author accepted your edit as written | Confirms the rules you applied; no new rule by itself |

Only the owner's own edits count as their writing. Overleaf's web edits each carry the editor's name, so a coauthor's edit, a
push by the loop or by another session or tool (any commit not titled "Update on Overleaf.", or "Update in editor." for a folder),
ends a window, and comments are undone before comparing. A closed thread whose file someone else also changed since the answer
was published reads "changed by others": it is not the owner's rewrite. The agent's text counts as the "before" side only once
it is in the file: an owner edit made before a later push (a rewrite approved in chat, say) is the owner's own edit, never a
revision of that later text. An older event with a `note` saying other people edited
in the same window may not be the owner's; learn from it only if it is clearly in their voice. If an event still is not the
author's writing, do not just
acknowledge it: `pairtex learn <slug> --discard <ids> --why "<reason>"` keeps it out of future analysis with the reason.

## From evidence to entries

For each event, ask what general move it shows, then do exactly one of these:

1. **Strengthen an existing entry.** Add the event id to its Evidence line (and a short before → after if it is a better example).
2. **Add a tentative pattern** (`### Tnn`) when the move is general: sentence shape, paragraph logic, how results are framed, hedging,
   length, notation habits. Write the pattern as an instruction, quote the author's words if any, and give one short before → after.
3. **Add a row to Words and phrasing** for a word-level preference (the author replaced "leverage" by "use" twice: prefer "use").
4. **Add to What … undid** for a reverted edit: what you did, what the author restored, why if it is clear.
5. **Project notes, not the style guide,** for anything specific to one paper: its terms, notation, which result is central,
   coauthor conventions. Write those in `projects/<slug>/NOTES.md`.
6. **Nothing**, for content changes (a new number, a fixed proof step, a moved figure), typo fixes and single-token changes with no
   pattern. Still acknowledge the event.

Comments count as evidence when they state a preference beyond the paragraph at hand. If the author writes it as a rule ("always",
"never", "以后", "不要再", "every time"), it goes straight to **Confirmed rules** with their words.

## Promotion and pruning

- **Tentative → Confirmed** after three independent pieces of evidence (different comments or paragraphs) with no counterexample,
  or when the author says it is general. Renumber it `Snn`, keep its evidence.
- **Contradicted** entries: note the counterexample under the entry. Two counterexamples: narrow the entry's scope or delete it.
- **Base rules** change only through the author. When a confirmed rule looks like a top-level principle, ask them in chat
  whether to add it to the base rules (or to a `base_style` file the project lists); do not edit those yourself.
- Keep the guide short. Merge entries that say the same thing. An entry is at most six lines. Examples are one short sentence each.

## Then

1. Add a dated line to the **Log** at the end of `STYLE.md` naming the events and what changed ("2026-11-08: E0012, E0014 → T07
   'state the regime before the result'; E0013 → What … undid").
2. `pairtex learn <slug> --ack <every id you processed, including the ones you skipped>` (it works while the watcher runs).
3. Commit the vault where it lives (`pairtex paths`; the data home is a git repository unless set up with `--no-git`):
   `git -C <data home> add -A <vault> && git -C <data home> commit -m "style: …"`.
4. In the chat report, name any new or promoted rule in one line, so the author can object.

## Using the guide

Read `STYLE.md` at the start of the loop and whenever its sha in the batch header changes. Apply it to the text you write or rewrite
for a comment. Do not restyle text the comment did not touch: a comment about one sentence is not licence to polish the section.
