---
name: pairtalk
description: PairTalk, talk slides as HTML (one file per slide, builds per click, a speaker view, a speaker script in SCRIPT.md) plus a live comment loop and the author's growing talk-style guide. The author and coauthors comment on any slide and click (with a marked box or a screenshot) or edit the script in the browser, on the author's computer or on an optional shared site; the session that runs this skill watches in the background, fixes the slides, replies under each comment, and learns how the author builds and gives talks from the edits they keep, rewrite or undo. Use when the author asks for talk slides, HTML slides, a conference or seminar talk, a job talk, a speaker script or speaker notes, to fix a talk from comments, to watch a talk (监听 talk, 盯着我的 comment, "watch mytalk", pairtalk), to seed the talk style from past talks (从我以前的 talk 学风格), or to read or update the talk-style file. Not for a report deck or an explainer nobody presents (PairDeck), and not for papers (PairTeX).
---

# PairTalk

A talk is a folder of HTML slides with a speaker script. The author reviews it in the browser: `c` opens the comment panel on
the current slide and click, where they can mark a box or attach a screenshot; `s` `s` opens the script, and any note can be
edited in place. A watcher that this session runs in the background exits when feedback is ready, which wakes the session;
the session fixes the slides, answers each comment, records what it made, learns from the evidence, and watches again.

```
pairtalk paths       # the CLI, on PATH via ~/.local/bin after install.sh; where the profile, style vault and talks are
```

Below, `$PT` stands for the CLI: `pairtalk`, or `~/.local/bin/pairtalk`, or `bin/pairtalk` next to this skill's folder.
`$PT <command> -h` lists the options. The skill works in any agent that reads `SKILL.md` files (Claude Code, Codex, ...).

| Path (`pairtalk paths`) | What it is |
| --- | --- |
| talk folder (`project.json` → `talk_dir`) | The talk: `index.html`, `slides/order.js`, `slides/*.js`, `SCRIPT.md`, the engine (`css/`, `js/`, `fonts/`, `vendor/`) |
| `projects/<talk>/NOTES.md` | This talk's facts, terms, venue and decisions. Read at start |
| talk style (`vault/STYLE.md`) | How the author builds and gives talks, growing. Read at start and when its sha changes |
| visual look (PairDeck's `STYLE.md`) | The author's palette, type and layout, when PairDeck is set up. It overrides the template's look |
| `references/playbook.md` | The built-in talk rules; STYLE.md overrides them |
| `references/qa.md` | How to check every click before the author sees it |
| `references/learning.md`, `references/seeding.md` | Turning evidence and past talks into STYLE.md entries |
| `references/cloudflare.md` | The optional shared site for coauthors |

The data home is `~/.pairtalk` (or `$PAIRTALK_HOME`). No profile yet: ask the author's name as coauthors see it and run
`$PT setup --name "…" --agent <your name>`.

## Build a talk

1. **Read** STYLE.md, the PairDeck look if `pairtalk paths` shows one, and `references/playbook.md`. Ask only what you cannot
   find: the slot in minutes, the venue and audience, the paper or results it presents.
2. **Make the folder:** `$PT new <talk> --title "…" --minutes <slot> --dir <where the author keeps talks>`. It copies the
   template (three starter slides) and registers the talk. `--example pagerank` copies the demo talk instead.
3. **Write `NOTES.md`** for the talk: the sources of every number, the paper's terms, the venue.
4. **Draft the storyboard** (playbook §2) in chat if the author wants to see it first; otherwise write the slides.
5. **Write the slides** in `slides/`, one file per slide, listed in `slides/order.js` (format below). Every click gets its
   note in the same file; the script budget is the slot times the author's words per minute.
6. **Check every click** (`references/qa.md`): `$PT shots <talk>`, then look at the screenshots, and run the playbook's
   checklist (§8).
7. `$PT snapshot <talk>`: this records the talk as you made it, so the author's later edits teach the style guide.
8. **Tell the author** in three lines: where the talk is, `pairtalk serve <talk>` to see it, and how to give feedback (`c` to
   comment on a slide and click, `s` `s` to edit the script, `v` for the speaker view). Offer to start the loop.

## The slide file format

```js
// slides/05_result.js: one slide; the comment says what it is for.
Deck.slide({
  id: 'RESULT1',                      // unique, letters, digits, - and _; comments and SCRIPT.md use it
  title: 'Faster refresh, larger swings',
  steps: 2,                           // the last click: this slide has clicks 0 (on entry), 1 and 2
  notes: [ "On entry …", "Click 1 …", "Click 2 …" ],   // one string per click; <b>…</b> marks a spoken cue
  html: `<div class="rows body" style="left:300px;top:320px;width:1320px">
           <div data-in="0">first</div><div data-in="1" data-dim="2">second</div><div data-in="2">third</div></div>`,
  init(el, L) { /* draw SVG with Deck.lib: L.svg(el), L.line, L.path, L.arrow, L.circle, L.rect, L.label, L.axes, L.icon */ },
  state: k => ({ t: k >= 1 ? 1 : 0 }),  // optional: numbers per click, tweened between clicks …
  draw(el, s, L) { /* … and drawn here from the tweened state */ },
  backup: false                       // true for backup slides, which go last in order.js
});
```

- Everything sits on a 1920 × 1080 stage that scales to the window; place with absolute pixels. Classes: `.rows`, `.body`
  (40 px), `.big` (48 px), `.small`, `.result` (a theorem box: `<span class="kind">Theorem</span>`), `.card`, `.pill`,
  colour classes `.c-blue`, `.c-gold`, `.c-teal`, `.c-orange`, `.c-green`, `.c-red`, `.c-purple`, `.c-ink2`. The title
  slide uses `kind: 'title'` with `.t-main`, `.t-rule`, `.t-sub`, `.t-who`.
- **Builds:** `data-in="k"` shows an element from click k on, `data-out="k"` hides it from click k, `data-dim="k"` fades it.
  Deck.lib shapes take the same flags as options (`{ in: 1, dim: 3, draw: true }`; `draw` strokes a line in).
- **Scope CSS to the slide:** `<style>.slide[data-id="RESULT1"] .x { … }</style>` inside `html`.
- **Maths:** `\\( … \\)` inside the template string (backslashes doubled). Colour a term with `\\class{c-blue}{…}`. The
  bundled fonts cover ordinary maths, sums, fractions, AMS symbols and calligraphic letters; avoid `\\mathbf` and very tall
  delimiters such as `cases`: their fonts are not bundled, and `shots` reports the missing font.
- **Shared code** for several slides goes in a file listed first in `order.js` that registers no slide (the demo's
  `00_web.js`). Images go in the talk folder (`assets/`) and are referenced relatively.
- `Deck.lib.SECTIONS = [...]` in `order.js` and `Deck.sectionCard({ id, index, title })` make section cards with an outline.

## Start the loop

1. **Pick the talk.** `$PT status` lists them; `$PT status <talk>` shows its folder, inbox and watcher.
2. **Read** STYLE.md, the PairDeck look, `preferences.md`, the talk's `NOTES.md`, and the playbook.
3. **Make sure the author can comment.** On their computer: ask them to run `pairtalk serve <talk>` in a terminal (or run it
   yourself in the background) and open the address it prints. For coauthors elsewhere: the shared site
   (`references/cloudflare.md`).
4. **Start the watcher in the background**, so that its exit wakes you: `$PT watch <talk>` (`--remote` for the shared site;
   in Claude Code, the Bash tool with `run_in_background: true`). An agent that cannot be woken by a background command runs
   `$PT watch <talk> --max-hours 0.5` in the foreground, or polls `$PT watch <talk> --once` every 30 to 60 seconds
   (`AGENTS.md`). It holds a lock, so only one session watches a talk; `--takeover` moves it here.
5. **Tell the author** in two lines: which talk you are watching, and how to comment.

**Authorization.** Starting the loop at the author's request authorizes edits to that talk's folder and replies to the
comments this loop receives, for this session, and `pairtalk publish` when the talk uses a shared site the author set up. It
does not authorize other talks, other files, or publishing anywhere else.

## Each batch

The watcher's exit wakes you. Exit 0: the batch is on stdout (and in `projects/<talk>/batches/`). Exit 2: the shared site is
unreachable: tell the author. Exit 4: the slides changed after the last batch without a snapshot: run `$PT snapshot <talk>`
if those were your edits, or `$PT watch <talk> --force` if the author made them. Exit 5: another session holds the talk.

1. **Read the batch.** Each comment has its id, slide id and number, click, author (owner or coauthor), text, the box in
   slide coordinates and the attachments' paths. Script edits show the before and after of each note. Re-read STYLE.md if its
   sha changed. Look at each comment's slide: `$PT shots <talk> --ids <SID> --click <k> --box x,y,w,h` draws the box.
2. **Fix each comment** in the slide's file, at its scope, and in every parallel place (playbook §6). A question gets an
   answer, and the slide changes so the next viewer does not ask.
3. **Script edits:** `$PT script apply <talk>` (`--remote` for the shared site) writes SCRIPT.md edits and the browser's
   edits into the slides. A conflict (you changed the same note) applies nothing: merge by hand and say so.
4. **Check** every click you changed (`references/qa.md`).
5. `$PT snapshot <talk>`: records what you made. For the shared site, `$PT publish <talk>` next.
6. **Answer each comment:** `$PT resolve <talk> <id> "reply"` (`--remote` for the shared site). The reply shows under the
   comment. When an owner's comment states a general preference without words like "always" or "never", add
   `--stated "<the rule, in their words>"`.
7. **Learn,** following `references/learning.md`: `$PT learn <talk>` shows the evidence; update STYLE.md (or NOTES.md for this
   talk only); `$PT learn --ack <ids>`; commit the vault.
8. **Restart** the watcher, then **report** to the author in two to four lines (in the language `preferences.md` asks for):
   the comments, what changed, any rule learned or promoted.

**Owner and coauthors.** The batch marks each comment and script edit as the owner's (the profile's name; on the review
server on the author's computer, also an unnamed comment) or a coauthor's. Fix and answer both. Only the owner's comments and
edits are style evidence; a coauthor's comment never becomes a rule, even when it says "always".

## Editing rules

- **Do what the comment asks, at its scope,** and leave everything else as it is.
- **Never change the science on your own.** Claims, numbers, results and figures' data change only when a comment asks and a
  source supports it. Otherwise answer in the reply.
- **Build in the author's style:** STYLE.md, then the playbook.
- **Keep the talk working:** every slide id unique, `order.js` lists every file, every click checked, no console errors.
- **A decision that is the author's** (two readings, a structural change): make no edit; reply with numbered options.

## Replies

English unless `preferences.md` says otherwise, one to three short sentences: what changed and where (slide ids, clicks), the
new wording when it is short, the parallel places. No boilerplate.

## Stop

When the author says stop, stop the background watcher, run `$PT learn <talk>` for a last pass, and say in a few lines what
the style guide gained this session.

## Seeding the style from past talks

When the author offers past talks, run `$PT seed <slides and scripts> --duration <minutes> --note "…"` (one talk per call
when durations differ) and follow `references/seeding.md`.

## Feedback about the loop

When the author comments on how the loop behaves (speed, replies, what it checks), record it in the vault's
`preferences.md` with their words and the rule, and commit the vault. Talk-style feedback goes in `STYLE.md` instead.
