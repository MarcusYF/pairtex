---
name: pairdeck
description: PairDeck builds animated, step-by-step HTML explainer decks (a visual intro to a paper, project, concept or proposal, a research or results report deck, a pitch) with colour-coded diagrams and charts that build up, one real interaction, light and dark mode and a phone layout; checks every slide on screenshots; and revises the deck in a live comment loop in which the author drags a box on a slide in a local review page and types. It keeps the author's visual style (palette, type, layout, density) in a style guide that learns from their comments and edits, and can start it from their past decks (.pptx, .pdf, .html). Use when the author asks for a visual explainer, an animated or interactive HTML deck, web slides that explain something, a report deck, to review, comment on or watch such a deck (pairdeck, "watch my deck"), or to seed or update their visual style guide. Not for Keynote or PowerPoint files, posters, a single static chart, or talks with a speaker script (PairTalk does those).
---

# PairDeck

A PairDeck deck is a short web deck (usually 6 to 10 slides) that explains one thing with pictures that build up step by
step: who acts, what flows where, what changes, and what it means. The engine (`assets/engine/`) handles layout, type, colour
roles, light and dark mode, builds, line drawing, growing bars, counters, navigation and the phone layout. Your part needs
judgement: understanding the material, choosing the story and the pictures, writing the slides, checking every slide, and
learning the author's taste.

```
pairdeck paths       # where the profile, style vault and decks are
```

Below, `$PD` is the CLI: `pairdeck`, or `~/.local/bin/pairdeck` when it is not on PATH, or `bin/pairdeck` next to this skill's
folder. `$PD <command> -h` lists the options. This skill works in any agent that reads `SKILL.md` files (Claude Code, Codex,
...); where a step depends on the agent, it says so.

| Path (`$PD paths`) | What it is |
| --- | --- |
| `vault/STYLE.md` | The author's visual style, growing. Read it before every deck and when its sha changes |
| `vault/preferences.md` | The author's feedback about the loop itself (report language, what to ask first, ...) |
| `vault/evidence.jsonl` | Raw style evidence, one event per line |
| `vault/seed/<id>/` | What `seed` read from the author's past decks: `samples.md`, `stats.json`, `pages/` |
| `projects/<slug>/` | Per deck: `project.json` (where the deck lives), `NOTES.md`, `comments.jsonl`, snapshots |
| `references/` | `style.md`, `components.md`, `content.md`, `qa.md`, `targets.md`, `learning.md`, `seeding.md` |

No profile yet: ask the author's name and run `$PD setup --name "…" --agent <your name: Claude, Codex, …>`.

## Before every deck

1. **Read `STYLE.md`** in full, then `preferences.md`, then the deck's `NOTES.md` if it exists. Order of authority: the
   author's request in front of you; the guide's base rules; its confirmed rules; its tentative patterns (where the case
   clearly fits); `references/style.md` and `content.md`; general good practice. Style never changes a claim or a number.
2. **The style guide is empty and the author has past decks?** Offer once to seed it: `$PD seed <files or folders>`, then
   follow `references/seeding.md`. Do not insist; the defaults are a good start.
3. **Settle four things**, from the request or with one short question if they are truly unclear: the material and where it
   comes from; the audience (default: a smart reader from another field); where the deck will live (`references/targets.md`;
   default a standalone folder); the language (default the author's).

## Build a deck

1. **Read the source in full and write a fact sheet:** every claim and number you might show, each with its location. The
   deck can say only what the sheet supports (`references/content.md`). Keep it next to the deck or in your scratch space.
2. **Storyboard before HTML.** Pick the story structure for the material (`content.md`). One line per slide: the headline (a
   finding, not a topic), the picture, the build steps, the facts it uses. Plan one genuine interaction. Every content slide
   needs a real diagram or chart; a slide of text alone is a sign to rethink it.
3. **Scaffold:** `$PD new <slug> --title "…" --subtitle "…" --meta "…" [--dir DIR]`. It writes `index.html` with the engine in
   `_deck/` and registers the deck. On an existing deck folder it only registers it, and its current version becomes the
   baseline.
4. **Write the slides** with the engine's components (`references/components.md`) in the visual language of
   `references/style.md`, as the author's `STYLE.md` adjusts it. Put this deck's colour mapping for its actors in `NOTES.md`.
5. **Check every slide:** `$PD qa <slug>` lints, checks the layout in a browser, and screenshots every slide fully built in
   light, dark and narrow mode (`--slides 3,5` to re-check, `--steps` for build order, `--after '<JS click>' --tag x` for an
   interaction state). **Open and look at every screenshot** (Claude Code: the Read tool; Codex: `view_image`) and go through
   the checklist in `references/qa.md`. Fix, repeat until a full pass is clean, then check the facts once more.
6. **Snapshot:** `$PD snapshot <slug> -m "first build"`. The author's later edits are compared with this version.
7. **Show it.** Start `$PD review <slug>` in the background (it serves the deck on 127.0.0.1 with the comment overlay; the
   deck file itself is never changed) and give the author its URL. Say in two lines how to comment: press **Comment** (or
   `c`), drag a box over what they mean (a click means the whole slide), type, Send; replies appear under each comment. Offer
   to start the loop.

## The comment loop

Start it when the author asks ("watch my deck", or yes to your offer):

1. `$PD status <slug>`. If comments are "with the agent" from an earlier session, handle them first (step 2 of each batch).
2. Make sure the review page runs (`$PD review <slug>` in the background; it keeps running between batches).
3. Start the watcher **in the background, so that its exit wakes you**: `$PD watch <slug>` (Claude Code: the Bash tool with
   `run_in_background: true`). It holds a lock: one watcher per deck; `--takeover` only when the author moves the loop to this
   session. An agent that cannot be woken by a background command runs `$PD watch <slug> --max-hours 0.5` in the foreground,
   or polls `$PD watch <slug> --once` every 30 to 60 seconds.
4. Tell the author in one line that you are watching, and where the review page is.

**Authorization.** Starting the loop at the author's request authorizes edits to this deck that answer the comments it
receives, for this session. It does not authorize publishing, deploying or sending the deck anywhere.

### Each batch

The watcher prints one batch and exits 0. Exit 4: the deck changed after you answered comments but you did not snapshot (run
`$PD snapshot <slug>`, then watch again). Exit 5: another session watches this deck. Exit 2: the deck file is missing.

1. **Read the batch.** For each comment: its id, slide, build step, the box (fractions of the slide's content area), the words
   under the box, the text, and any earlier thread. For each of the author's own edits: a diff against your last snapshot.
   Re-read `STYLE.md` if its sha changed.
2. **For each comment, in order:** edit the deck, then `$PD resolve <slug> <id> "<reply>"`. The reply appears under the comment
   on the review page. If a comment states a general preference the watcher did not mark as `stated` (it marks "always",
   "never", "from now on" and the like), add `--stated`.
3. **Check what you changed:** `$PD qa <slug> --slides N,M` and look at the screenshots. The review page reloads by itself when
   the deck changes on disk.
4. **Snapshot:** `$PD snapshot <slug> -m "c3, c4"`. Do this before you watch again.
5. **Learn** (`references/learning.md`): `$PD learn <slug>` shows every pending event in full. Update `STYLE.md`, then
   `$PD learn --ack <ids>`; an event that is not the author's (a test, another person's edit) gets
   `$PD learn --discard <ids> --why "…"`. Commit the vault: `git -C <data home> add -A && git -C <data home> commit -m "style: …"`.
6. **Watch again** the way you started, and **report** in two to four lines, in the language `preferences.md` asks for (else
   the author's): what changed, any rule learned or promoted (so the author can object), anything that needs them.

### Editing rules

- **Do what the comment asks, at its scope.** The box and the words under it say what "this" is. Leave other slides alone.
- **One comment, every parallel place.** If the fix applies elsewhere (the same actor's colour, the same chart style, the same
  term), apply it there too and say where in the reply.
- **Never change the facts on your own.** Numbers, claims and sources change only when the comment asks and the fact sheet
  supports it. Otherwise answer in the reply.
- **A decision that is the author's** (two good layouts, a cut that loses content): make no edit; reply with the options
  numbered. The author answers with a follow-up.
- **Keep the deck working:** no new files unless asked, no hard-coded colours (use the engine's classes), builds still in reading
  order.

**Replies** are one to three short sentences: what changed and where (slide numbers), and one alternative only if it is worth
the author's time. The author presses **Keep** on an answer they accept as made (that is `kept` evidence), or **Follow up**.

## Accuracy

Every number and claim on a slide comes from the fact sheet. A value read off a figure shows "≈" and says "approximate".
Invented curves and toy examples say "illustration" or "schematic". Keep the source's qualifiers ("in simulations", "in the
worst case"). Your own inferences may appear, labelled as yours. Details: `references/content.md`.

## Deliver

- **One file:** `$PD bundle <slug>` writes `dist/<slug>.html` in the deck's folder with the engine, icons, images and fonts
  inlined (about 0.6 MB; `--no-fonts` for under 0.1 MB). Run `$PD qa <that file>` too.
- **A share image** for a public URL with Open Graph tags: `$PD card <slug>`.
- Other targets (a website that hosts the engine once, a course page): `references/targets.md`.
- Publishing, deploying or sending the deck needs the author's explicit go-ahead.

## Host notes

- **Claude Code.** Run `review` and `watch` with `run_in_background: true`. To click through the deck yourself, open the review
  URL in the browser pane if one is available (`preview_start` with the URL); use its mobile preset for the phone layout. A
  hidden pane throttles timers, so judge timed animations with `qa --after` instead.
- **Codex.** Look at screenshots with `view_image`. If background commands cannot wake you, poll `$PD watch <slug> --once`.
  Invocation: `$pairdeck`.

## Stop

When the author says stop, stop the background watcher (leave the review page running if they still read the deck, else stop
it too), run `$PD learn <slug>` for a last pass, and say in a few lines what the style guide gained this session.

## Feedback about the loop

When the author comments on how the loop behaves (speed, replies, what it asks, how it reports), record it in `preferences.md`
in the vault with their words and the rule, and commit the vault. Visual-style feedback goes in `STYLE.md` instead.

## Files

- `references/style.md`: the visual language (canvas, type, colour roles, icons, diagram craft, charts, motion, slide
  patterns, words, what to avoid).
- `references/components.md`: the engine's markup and API (steps, dimming, animations, interactions, `Deck` hooks, icons).
- `references/content.md`: accuracy, the fact sheet, and story structures for papers, overviews, course concepts, projects,
  proposals, reports and experiment results.
- `references/qa.md`: the visual and factual checklist, and how to read `qa` output.
- `references/targets.md`: a standalone folder, one file, a website or course page.
- `references/learning.md`: turning evidence into `STYLE.md` entries.
- `references/seeding.md`: starting `STYLE.md` from the author's past decks.
- `assets/engine/`: `deck.css`, `deck.js`, `icons.svg`, and the Computer Modern fonts (SIL Open Font License, `fonts/OFL.txt`).
- `assets/template.html`: the page `new` starts from.
