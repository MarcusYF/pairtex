# Roadmap

PairTeX (then called overleaf-writer) was at 0.3.2 when this plan was written: two papers, one session per paper, one author. The three releases make it
something to share: first with coauthors, then as an open-source tool for researchers who write in Overleaf or in a local LaTeX
editor.

## What it is for

Two features carry the tool, and every release serves them:

1. **A style vault.** The agent's writing comes closer to the author's own with use, because it learns from the edits the author
   keeps, rewrites or undoes, and from the preferences the author states in comments.
2. **Comments handled in the editor.** The author types a comment where the problem is and keeps writing; the edit and the reply
   arrive in the same document. No copying text into a chat and back.

## What earns a feature

- **A comment cannot do it alone.** Most requests already are comments: draft a section from bullet points, critique a section as
  a reviewer would, turn a note in Chinese into a paragraph. These go into the README as examples. A feature is built only when
  it needs something a comment cannot give the agent: state that persists (the vault, a notation ledger), a hard check (a science
  receipt, a submission check), a new data source (bibliographic databases), or a new place to write (a local editor).
- **The author stays in the editor.** Two markers and `..`; nothing more to learn.
- **Every change is visible, attributed and revertible.** The agent's edits are ordinary commits, its replies sit next to the text,
  and nothing changes the science unnoticed.
- **Personal data stays personal.** Paper text, style evidence and project ids never enter the shared repository.

## Where it stands (0.3.2)

- **Protocol.** `%!` asks for a change, `%?` asks a question, `[[ ]]` marks part of a paragraph, `..` sends. Replies become green
  `\claude` notes, or `%` lines where a note cannot go.
- **Push.** A compile check that blocks only new LaTeX errors; guards for new files, protected notes and threads; a merge with the
  author's concurrent typing; patch and redo on a real conflict.
- **Learning.** Evidence from runs of web edits, from kept, rewritten and undone edits, and from stated preferences. A tentative
  pattern is confirmed after three independent pieces of evidence.
- **What blocks sharing** is listed under 0.4.

## 0.4: shareable

The gate for giving the tool to coauthors. Nothing here changes how the loop behaves for its current user; it removes what ties
the tool to one person, one machine and one backend.

**Status (0.4.0, 2026-11-08).** Items 1 to 7 are in, with tests (`CHANGELOG.md`), and the first installation's data has moved
to its data home. Decided on 2026-11-08: the name PairTeX and the MIT license (0.4.1). Published on 2026-11-09 (0.4.2) from a
new repository with fresh history: https://github.com/MarcusYF/pairtex.

### 1. A user profile instead of one name

- **Why.** `bin/ow` named its first user 37 times, the note macro printed that name, the style seed was a path in one person's home folder, and
  the skill and the learning notes address one author.
- **Plan.** `pairtex setup` writes `profile.json`: name, a short handle for notes, the vault's location, the default notes mode.
  Prompts, batches and notes use the profile. Each project keeps `owner_name`, checked against the profile.
- **Done when** a fresh profile passes the end-to-end test and the code names no person outside examples.

### 2. Personal data out of the repository

- **Why.** The repository tracks `style/STYLE.md`, `style/evidence.jsonl` (with excerpts of unpublished papers) and each project's
  `NOTES.md` and `project.json` (Overleaf ids, private paths). Its git history holds all of them.
- **Plan.** A data home outside the code, `~/.pairtex/` (or `$PAIRTEX_HOME`), with `vault/`, `projects/` and `profile.json`.
  The repository ships the code, the skill, templates (`STYLE.template.md`, `NOTES.template.md`) and the tests. `pairtex migrate` moves
  the current data there. Publish from a new repository with fresh history, not from this one.
- **Done when** a clone of the public repository holds no paper text, project id or private path, and the existing loops run
  unchanged after `pairtex migrate`.

### 3. Comments and learning by author

- **Why.** The watch lock is a file on one machine. If two coauthors each run a loop on the same project, both take every
  comment, edit for it and push. Coauthors' web edits are only flagged ("may not be the owner's"), so a shared project mixes their
  writing into one vault.
- **It can be done.** Overleaf's web-edit commits carry the editor's real name. On one three-author project: 66, 7 and 6 commits
  by the three authors, and 1 by "Anonymous" (an edit through a sharing link).
- **Plan.**
  - A comment's author is the author of the commit that added its lines (`git blame` at the fetched head).
  - A loop handles its owner's comments. `"comments_from"` adds named coauthors who run no loop of their own; a coauthor who runs
    a loop and is also listed in another loop's `comments_from` is a configuration error the watcher reports.
  - Runs of web edits are split by author. Each author's edits are evidence for their own vault only; edits by others and by
    "Anonymous" are never evidence.
  - Notes print the commenter's handle: "[c7] Grace: … Claude: …".
  - Check whether Overleaf ever folds two people's edits into one commit. If it does, treat that run as mixed, as now.
- **Done when** a test with two simulated authors and two loops on one remote handles each comment exactly once, by its author's
  loop, and each vault holds only its owner's evidence.

### 4. Backends beyond Overleaf

- **Why.** Overleaf's git integration is a premium feature: every member of a project whose owner has a premium plan can use it,
  and no one else. Authors who write in VS Code, TeXstudio or Emacs, often with the paper on GitHub, have no Overleaf project at
  all.
- **Plan.** One backend interface (fetch the head, read, write, publish), with three backends:
  - `overleaf`: the current git bridge.
  - `git`: any git remote (GitHub, GitLab). The same code path with another remote; runs of web edits become runs of the
    author's own commits.
  - `folder`: a local folder the editor saves into. The watcher polls file contents; publishing writes the file, and a shadow git
    repository keeps every version so any edit can be reverted. A file is written only if it has not changed since it was read;
    otherwise the edit is redone on the new text, as after an Overleaf conflict. The docs give each editor's setting for
    reloading a file changed on disk.
- **Done when** the end-to-end test runs against all three.

### 5. The project's own compiler

- **Why.** The compile check runs `latexmk -pdf` (pdfLaTeX). Papers built with XeLaTeX or LuaLaTeX, common with CJK text or
  custom fonts, are misjudged, and notes treat Chinese as unprintable.
- **Plan.** `"compiler": "pdflatex" | "xelatex" | "lualatex"` per project, read from the project's `latexmkrc` when it has one.
  Under XeLaTeX and LuaLaTeX, notes print CJK text directly.
- **Done when** the test compiles a XeLaTeX project with a note in Chinese.

### 6. A submission check and a clean copy

- **Why.** The tool writes conversations into the paper: notes print in the PDF, threads stay in the source, and arXiv publishes
  the source with its `%` comments.
- **Plan.**
  - `pairtex check SLUG` lists what is left: `\claude` notes, `%!` and `%?` comments and threads, `[[ ]]` brackets, and protected
    coauthor notes.
  - A project setting (one line in the preamble) hides all notes in the PDF at once, for sending a draft out.
  - `pairtex clean SLUG --out DIR` writes a copy without notes, comments, brackets or the `\claude` definition, ready for arXiv or a
    journal. arxiv-latex-cleaner can then shrink the figures.
- **Done when** the clean copy compiles to the same pages minus the notes, and contains no `%` comment, `\claude` or `[[`.

### 7. Docs and install for someone else

- **Any agent.** `pairtex` needs no particular agent: the watcher exits and the waiting session wakes. An `AGENTS.md` beside the Claude
  Code skill lets Codex users run the same loop.
- **A README for a newcomer**: what it does, a five-minute start, the comment cheat sheet, and what is sent where.
- **Credentials** through the macOS keychain, Git Credential Manager or libsecret. `pairtex` never stores a token.
- **Platforms**: macOS and Linux; Windows through WSL (`pairtex` uses `fcntl`).
- **A license** (an open decision, below).

## 0.5: trust and the vault

### 8. A science receipt for every push

- **Why.** "Never change the science on your own" is a rule for the agent, not a check. Coauthors will let an agent push to a
  shared paper only if they can see at a glance that results and statements did not move.
- **Plan.** At push, compare each comment's edit for:
  - numbers in text and tables;
  - display and inline maths;
  - the text of theorem-like environments (theorem, lemma, proposition, corollary, assumption, definition);
  - `\cite` keys;
  - `\label` and `\ref` targets.

  The receipt goes in the push output, and one short line goes into the note ("Changed: Eq. (3); Assumption 2; cite
  +smith2024"). In strict mode, set per project, such changes block unless the comment asked for them (`--allow-science`).
- **Done when** a test edit that changes a number and a theorem condition gets a receipt naming both, and strict mode blocks it.

### 9. Citations that exist

- **Why.** An invented reference is the most damaging mistake an AI writing tool can make. And keeping a `.bib` correct is tedious
  work that authors already do by hand.
- **Plan.**
  - **Adding a citation.** On `%! cite ..`, the agent finds the work in Crossref, DBLP, arXiv or Semantic Scholar and inserts the
    BibTeX from that source, never from memory. The reply names the source.
  - **Checking the bibliography.** `pairtex cite check SLUG` resolves every cited entry by DOI, arXiv id or title. It reports:
    - entries not found;
    - wrong titles, authors or years;
    - arXiv preprints that now have a published version;
    - duplicates under two keys;
    - keys that are cited but missing.
  - **What leaves the machine.** Only bibliographic metadata: titles, DOIs and ids.
- **Done when** an invented entry and a superseded preprint in a test `.bib` are both reported. The test replays recorded
  responses, so it needs no network.

### 10. The vault, for a new author

- **Cold start.** `pairtex style seed` builds a first vault from two sources:
  - **Past projects.** It replays the author's past Overleaf or git projects and takes the author's own edits as evidence. Rewrites
    of a coauthor's text are the strongest signal of all.
  - **Published papers.** It reads the author's published `.tex` sources for phrasing, as tentative patterns only.
- **Layers.** The vault is read in four layers; the more specific one wins:
  1. **Group conventions**: notation macros, spelling, "we", terms. A small file a lab shares in its own repository.
  2. **The author's style.**
  3. **Venue conventions**: JMLR, NeurIPS.
  4. **The paper's `NOTES.md`.**

  The group layer holds conventions, not prose style, so it never overrules the author's voice.
- **Export.** `pairtex style card` writes a compact version to paste into any other AI tool:
  - the confirmed rules;
  - the tentative patterns, one line each;
  - words to use and to avoid;
  - what the author undid.
- **Done when** a vault seeded from a test author's two-project history holds patterns from that author's edits only.

## 0.6: deadlines and consistency

### 11. A page budget

- **After every push.** The push reports:
  - the page count, in total and for the main body (up to the bibliography or a configured label);
  - the change from Overleaf's version;
  - a warning above the venue's `page_limit`;
  - new overfull boxes larger than a few points.
- **On `%! fit in 9 pages..`** the batch includes each section's share of the pages. The agent replies with numbered options for
  cuts, since cutting content is the author's decision, and then makes the cuts the author chose.

### 12. A notation and term ledger

- **The ledger.** Each paper keeps one (`NOTATION.md`): every symbol and term, where it is defined, and what it means. It is
  seeded from `\newcommand`s and definitions and updated after each batch.
- **In the batch.** The batch shows the ledger entries for the symbols in the commented paragraph.
- **The check.** It reports symbols used before their definition, one symbol with two meanings, and one concept with two names.
  Theory papers written by several people drift here most.

### 13. A digest for coauthors

`pairtex digest SLUG --since DATE` produces, for an advisor or coauthor who did not watch the session:
- a latexdiff PDF of what changed;
- each comment, with its reply and its commit;
- the threads still open.

## Later

Useful, but not needed for the first public version:

- **Review responses.** Map reviewers' points to places in the paper, link each change to its point, and draft the response letter
  from them.
- **Numbers from results.** Link table cells to the experiment output they come from, and check for stale numbers.

## Not planned

- **Shortcut markers** (`%!t` for "tighten"). Natural language already says it, and two markers are what make the protocol easy
  to remember.
- **Overleaf's comment bubbles.** They are not in the git history. Reading them would mean automating the Overleaf web page, which
  breaks whenever the page changes.
- **A chat window or a web front end.** The point is not to leave the editor.
- **Whole-paper polish without comments.** With no comment there is no scope, and nothing for the vault to learn from.

## Open decisions

1. **License.** MIT (decided 2026-11-08).
2. **The public repository.** Named PairTeX (decided 2026-11-08); public at https://github.com/MarcusYF/pairtex since
   2026-11-09 (0.4.2), published from a copy with fresh history.
3. **Notes for new users.** Visible green notes (the current default) or `%` lines.
4. **Which comments a loop handles.** Its owner's only (recommended), or everyone's when a project has a single loop.
5. **Install.** `git clone` and `install.sh`, or a `pipx` package.
