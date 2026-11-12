# The style vault: one contract, three tools

PairTeX (writing), PairDeck (report decks) and PairTalk (talks) each keep a **style vault**: a folder the author owns, outside
this repository, in which the tool remembers how the author writes, designs and presents. The three tools share one contract,
so a researcher who knows one knows all three. This page is that contract. Each tool's own `skill/references/learning.md` and
`skill/references/seeding.md` say how its agent applies it.

## 1. What every tool provides

| Piece | Contract |
| --- | --- |
| **Data home** | `~/.<tool>` (`~/.pairtex`, `~/.pairdeck`, `~/.pairtalk`), or `$<TOOL>_HOME`. Never inside the code folder. A git repository unless set up with `--no-git`, so every change to the vault is a commit the author can read and revert. |
| **No model of its own** | The CLI is deterministic plumbing (standard library, plus git, Chrome or Node where the tool needs them). All judgement runs in the coding agent the author already uses (Claude Code, Codex, or any agent that runs shell commands), on the author's own plan. No API key, no server of ours. |
| **Skill** | `<tool>/skill/SKILL.md` plus `references/`, linked by `install.sh` into `~/.claude/skills/<tool>` (Claude Code) and `~/.agents/skills/<tool>` (Codex and other agents that read the open agent-skills format). |
| **Commands** | `setup`, `paths`, `status`, `seed`, `learn`, and a feedback loop: `watch` (waits for the author's feedback, prints one batch, exits) and `resolve` (answers one item). Same names and flags in every tool. |

## 2. The vault

```
~/.<tool>/
  profile.json          name (as coauthors see it), handle, agent name, language for chat reports
  vault/
    STYLE.md            the living guide (sections below); the agent reads it before every piece of work
    evidence.jsonl      one JSON object per event, append-only except for status marks
    seed/<seed-id>/     what `seed` extracted from the author's past work: manifest.json, stats.json, samples.md, pages/
    preferences.md      how the loop should behave (speed, report language, what to ask first); not style
  projects/<slug>/      per paper, deck or talk: state, snapshots of the agent's last version, NOTES.md
```

`STYLE.md` has the same skeleton in every tool; only the domain table differs:

1. **Base rules**: principles the author confirmed. Only the author adds or changes them.
2. **Confirmed rules** (`S01`, `S02`, ...): three or more independent pieces of evidence and no counterexample, or stated by the
   author as general ("always", "never", "以后都").
3. **Tentative patterns** (`T01`, ...): seen once or twice; applied only where the case clearly fits.
4. **Domain table**: *Words and phrasing* (PairTeX), *Palette, type and layout* (PairDeck), *Pacing and script* (PairTalk).
5. **What the author undid**: edits the author reverted. Never repeat them.
6. **Log**: one dated line per learning pass, naming the events and what changed.

Order of authority, highest first: the author's request in front of the agent; base rules; confirmed rules; tentative patterns;
the tool's built-in defaults (its `references/style.md` or playbook); general good practice. Facts bound all of these: **style
never changes a claim, a number or a result.**

## 3. Evidence

Every event in `evidence.jsonl` has `id` (`E0001`, ...), `date` (ISO 8601 with offset), `kind`, `project` (a slug, or `null`
for a seed), and kind-specific fields. Kinds, strongest first:

| Kind | What happened |
| --- | --- |
| `revised` | The author rewrote what the agent made (text, a slide, a script line). `before` is the agent's version, `after` the author's. |
| `reverted` | The author undid the agent's change. |
| `stated` | A comment states a preference beyond the item at hand ("too dense", "never use a pie chart"). |
| `own_edit` | The author's own new work in the editor, when it shows a habit rather than content. |
| `seed` | One past work the author gave to `seed` (a paper, a deck, a talk): its stats and samples. |
| `kept` | The author accepted the agent's version as made. Confirms rules; adds none by itself. |

Only the owner's own actions count. A coauthor's comment or edit, a push by another session or tool, and the agent's own output
are never the owner's style. `learn --discard <ids> --why "<reason>"` keeps such an event out of every later pass;
`learn --ack <ids>` marks events as processed. Both work while the watcher runs, and both only add `status`/`why` fields: the
log is never rewritten otherwise.

## 4. Seeding: start from the author's own work

`<tool> seed <files or folders> [--note "..."]` turns a batch of the author's past work into evidence, so the first draft is
already close:

| Tool | Accepts | Extracts (into `vault/seed/<seed-id>/`) |
| --- | --- | --- |
| PairTeX | `.tex` projects and `.pdf` papers the author wrote (mostly) alone | prose paragraphs by section, sentence-length and paragraph-length profile, frequent openings, hedges, connectives, person and tense, macros and notation habits |
| PairDeck | `.pptx`, `.pdf` exports of slides, `.html` decks (`.key`: export to PDF or PPTX first) | rendered page images, palette with frequencies, fonts, words per slide, slide count, titles and text, layout counts |
| PairTalk | the same, plus speaker notes, `SCRIPT.md` files and talk durations | as PairDeck, plus script length per slide, words per minute when a duration is given, how talks open and close |

Then the agent reads `samples.md`, `stats.json` and the page images, and drafts entries in `STYLE.md` following the tool's
`references/seeding.md`:

- each seeded work is one independent piece of evidence (`seed` event, one per file);
- a pattern clear in **three or more** seeded works may enter as a confirmed rule, its evidence line saying `(seed)`; fewer
  goes in as tentative;
- content (topics, results, names) never becomes a rule, only how it is written, designed or presented;
- the agent then shows the author, in chat, the five to ten strongest entries, and the author may delete or edit any.

Seeding reads files on the author's computer and writes only into the data home. `seed --list` shows past seeds;
`seed --forget <seed-id>` deletes one with its events.

## 5. The feedback loop and learning

Each tool's loop has the same shape:

1. The author gives feedback where the work lives: `%!` comments in the `.tex` source (PairTeX), comments on a slide in the
   local review page (PairDeck), comments on the talk site or in the inbox file, and script edits (PairTalk).
2. `watch` notices, waits until the feedback is settled, prints one batch and exits. That exit wakes the agent session that
   started it in the background.
3. The agent fixes the work, answers each item with `resolve`, publishes, and records `snapshot` of what it made so the
   author's later edits can be compared with it.
4. The agent runs a **learning pass** on the batch's evidence (`learn` lists it): strengthen an entry, add a tentative pattern,
   add a row to the domain table, record an undo, or nothing for content-only changes. Then `learn --ack`, and commit the vault.
5. It reports in two to four lines, naming any new or promoted rule so the author can object, and starts `watch` again.

## 6. Privacy

The author's work, its text and images, the evidence and the style guide stay in the data home on the author's computer. They
never enter this repository, its tests or its examples, and no tool sends them anywhere except to the coding agent the author
chose and to the place the author publishes to (Overleaf, their git remote, their own Cloudflare site).
