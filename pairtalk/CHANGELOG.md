# Changelog

## 0.1.0 (2026-11-12)

First version: talk slides as HTML, a comment loop with your coding agent, and a talk-style guide that learns from you.
Built on [html-slide](https://github.com/Yanwei-Sun/html-slide) by Yanwei Sun (see NOTICE.md).
- **A talk is a folder.** `pairtalk new` copies the engine (a 1920 × 1080 stage, builds per click, a speaker view with the next
  click, the note and a timer, an overview, print modes, MathJax 3 with its fonts) and starter slides, or the demo talk
  (`--example pagerank`: eleven slides and a backup, a theorem, two charts, an eight-minute script). One file per slide, one
  speaker note per click, kept in step with `SCRIPT.md`.
- **Review on your computer.** `pairtalk serve` shows the talk with the comment panel: comment on a slide and click, mark a
  box, attach screenshots, edit the script in place. Comments and edits carry the writer's name.
- **The loop.** `pairtalk watch` waits for settled comments, script edits (in `SCRIPT.md` or the browser) and the owner's own
  slide edits, prints one batch and exits; a lock per talk, `--takeover`. `resolve` answers a comment under it; `script apply`
  writes the edits into the slides; `snapshot` records what the agent made, and `watch` refuses to run (exit 4) when the agent's
  edits were not recorded.
- **The style vault**, per the suite's contract: `setup`, `paths`, `status`, `learn` (`--ack`, `--discard --why`). Evidence:
  `revised` (the owner rewrote the agent's note or slide), `reverted` (the owner restored what the agent replaced), `stated`
  (the owner's comment says "always", "never", …, or `resolve --stated`), `own_edit`, `seed`. Only the owner's comments and
  edits count; coauthors' are fixed and answered. `STYLE.md` has a *Pacing and script* table. PairDeck's style guide, when
  present, gives the visual look.
- **Seeding.** `pairtalk seed` runs the suite's visual extractor and reads speaker notes from `.pptx`, PairTalk folders and
  scripts: words per slide, words per minute (`--duration`), how talks open and close; one `seed` event per file; `--list`,
  `--forget`.
- **The shared site (optional)**: Cloudflare Pages Functions with a passcode gate and D1, staged in the data home by
  `pairtalk publish` (`--dev` runs it locally); `watch`, `resolve` and `script apply` take `--remote`.
- **The skill** for Claude Code and Codex, with a built-in talk playbook, and references for learning, seeding, checking every
  click, and the shared site. `AGENTS.md` lets an agent install PairTalk for the user.
- Tests: 83 end-to-end checks with a temporary home (including the shared site against a stand-in for Wrangler and D1), and 97
  offline checks of the site's middleware.
