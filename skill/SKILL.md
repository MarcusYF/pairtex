---
name: pairtex
description: PairTeX, a live comment loop on a LaTeX paper (an Overleaf project through its git bridge, any git remote, or a local folder edited in VS Code, TeXstudio, Emacs...), plus the author's growing writing-style guide. The author writes `%! ...` change requests and `%? ...` questions (optionally about a `[[bracketed]]` part of a paragraph) in the LaTeX source; the session that runs this skill watches the paper in the background, edits the LaTeX or, for a question, only answers, replies in a green note next to each comment, publishes at once, and learns the author's style from the edits they keep, rewrite or undo. Use when the author asks to watch or listen to a paper (监听 overleaf, 盯着我的 comment, 实时改 overleaf, 边写边推, "watch mypaper", pairtex, overleaf-writer), to add a paper to the loop, to stop it, to check a paper before submission (pairtex check / clean), or to read or update the writing-style file (写作风格文件, style guide). Not for a one-off edit with a PDF preview and approval, and not for slides.
---

# PairTeX

The author comments in the LaTeX source; a watcher that this session runs in the background exits when a comment is ready, which
wakes the session; the session fixes the text, replies next to the comment, publishes, learns from the evidence, and starts the
watcher again.

```
pairtex paths       # the CLI, on PATH via ~/.local/bin after install.sh; where the profile, style vault and projects are
```

Below, `$PT` stands for the CLI: `pairtex`, or `~/.local/bin/pairtex` when it is not on PATH, or `bin/pairtex` next to this
skill's folder (`ow` is its old name). `$PT <command> -h` lists the options. The skill works in any agent that reads
`SKILL.md` files (Claude Code, Codex, ...); where a step depends on the agent, it says so.

| Path (`pairtex paths`) | What it is |
| --- | --- |
| `projects/<slug>/repo/` | The loop's own checkout of the paper. Edit here, nowhere else |
| `projects/<slug>/NOTES.md` | Paper-specific rules, terms, facts files. Read at start |
| `projects/<slug>/project.json` | Backend, main file, owner, protected note macros, `comments_from`, `base_style` files |
| style guide (`STYLE.md`) | The author's writing style, growing. Read at start and when its sha changes |
| evidence (`evidence.jsonl`) | Raw style evidence, one event per line |
| loop preferences (`preferences.md`) | The author's feedback about the loop itself (reply language, report length, ...) |
| `references/learning.md` | How to turn evidence into style-guide entries |

The data home (profile, vault, projects) is `~/.pairtex` (or `$PAIRTEX_HOME`; `~/.overleaf-writer` from 0.4.0 still
works). An install from before 0.4 keeps it next to the code; `pairtex paths` says so, and `pairtex migrate` moves it out once every watcher is stopped and no comment is half answered.

## The comment protocol (what the author types)

```
%! make this paragraph tighter..        a change request, sent once it ends with ".." (may run on over %! or % lines)
%? why is this sentence here?..         a question: answer it, change no text
... sentence. %! say how often..        at the end of a line it refers to that line
... [[one sentence]] ... %! too long..  [[ ]] (or 【 】) marks the part of the paragraph a comment is about
\claude{c7}{make this ...}{Cut ...}      after you handle it: one green note line in the PDF (written by `pairtex resolve`)
\claude[Grace]{c8}{...}{...}                a note for a comment by someone other than the note macro's default name
%!c7 ... / %!c7> ...                    the same thread in % lines, where a note cannot go (maths, tables, captions)
```

`%@` is the 0.1 marker and still means a change request. `...` is an ellipsis and does not end a comment. The commenter deletes
the note line (or a thread's `%` lines) to accept it, or writes a new `%! … ..` or `%? … ..` line directly under it to follow up
(the batch then shows the thread's history). Protected note macros (`protected_macros`, e.g. `\ada{...}`) are notes to coauthors,
not requests: never act on or remove them unless a comment says so. Never delete a `\claude{…}` note yourself: only the commenter
accepts.

**Several authors.** The loop answers its owner's comments (the profile's name), and those of coauthors listed in
`comments_from`. A comment by anyone else is left to them: their own loop answers it, with its own id prefix (`grace3`), and
`pairtex status` lists it. The batch marks a comment by a listed coauthor "from <name>"; write that reply to them. Only the owner's
own edits and closed threads are style evidence.

## Start the loop

1. **Pick the project.** `ls` the projects folder from `pairtex paths`, then `$PT status <slug>`. No profile yet: ask the author for
   their name as their editor shows it to coauthors (the Overleaf account name) and run `$PT setup --name "…"`. For a new paper,
   one of:
   - `$PT init <slug> --overleaf <project id> --main <path/to/main.tex> --protect <note macros> --title "<title>"`
   - `$PT init <slug> --git <url> --main …` (any git remote; the author's own commits are their edits)
   - `$PT init <slug> --folder <dir> --main …` (a local folder the author's editor saves into)

   Then write `NOTES.md` (the template is there): the facts or results files, the paper's terms, the rules from the project's own
   guidelines that bind edits.
2. **Read** `STYLE.md`, `preferences.md`, the project's `NOTES.md`, and once per session the `base_style` files in `project.json`.
3. **Finish leftovers.** If status says "to finish first", run `$PT show <slug>` and handle those comments (step 2 below) first.
4. **Start the watcher** in the background, so that its exit wakes you: `$PT watch <slug>` (in Claude Code, the Bash tool with
   `run_in_background: true`). An agent that cannot be woken by a background command runs `$PT watch <slug> --max-hours 0.5` in
   the foreground, or polls `$PT watch <slug> --once` every 30 to 60 seconds (`AGENTS.md` in the repository). It holds a lock, so
   only one session watches a project on this machine. Use `--takeover` only when the author moves the loop to this session.
5. **Tell the author** in two lines: which project and file you are watching, and how to comment (`%! … ..` to change, `%? … ..`
   to ask, `[[ ]]` around the words meant; `..` sends it). For a folder: save the file to send a comment, and let the editor reload
   files changed on disk (VS Code does; Emacs needs `global-auto-revert-mode`).

**Authorization.** Starting the loop at the author's request authorizes `pairtex push` of edits and replies that answer the comments
this loop receives, in that project, for this session. It does not authorize other changes, other projects, force pushes, or
edits beyond what the comments ask. If a project's own rules require a preview and approval before every push, the author's
request to run the loop must say it is an exception; record that in NOTES.md.

## Each batch

The watcher's exit wakes you. Exit 0: the batch is on stdout (and in `projects/<slug>/batches/`). Exit 2: the paper is
unreachable or authentication failed: tell the author and do not restart blindly. Exit 4: the checkout has unpublished edits:
publish or inspect them. Exit 5: another session holds the project.

1. **Read the batch.** It gives each comment's id, file, line, section, author when not the owner, text, the paragraph it refers
   to and any thread history. Re-read STYLE.md if its sha changed. Open the file around each comment when its scope is larger than
   the excerpt.
2. **For each comment, in order:** edit `projects/<slug>/repo/`, then immediately `$PT resolve <slug> <id> "<reply>"`. The tool
   attributes the edits since the previous resolve to this comment, so finish one comment before starting the next. A change
   request that needs no edit (a choice for the author) is resolved with the answer alone.
   **Bracketed part.** The batch names the words inside `[[ ]]`: the comment is about exactly those. Edit between the brackets and
   leave them in place; `resolve` removes them and quotes the words in the thread.
   **Questions (`%?`, marked "question" in the batch).** Answer in the reply and change no text: `resolve` refuses a question
   whose paragraphs changed since the batch (exit 7). Pass `--allow-edit` only when the question itself asks for the change. See
   "Answering a question" below.
   **The thread becomes a green note** (`\claude{id}{the comment}{your reply}`) where the comment was, unless the place cannot
   hold one (maths, tables, macro arguments, the preamble): then it stays in `%` lines. `resolve` adds the macro to the preamble
   the first time, names the commenter when they are not the macro's default, and makes the text safe for LaTeX. Text the engine
   cannot print (Chinese under pdfLaTeX) stays in a `%` line above the note; under XeLaTeX or LuaLaTeX with a CJK package it goes in
   the note.
   **Mid-line comments.** When the author types `%!` or `%?` inside a sentence, the batch shows the line as it was and which last
   words of the comment are the line's own prose (now hidden from the PDF). Put those words back in the sentence before the
   marker, and leave the `%! …` text itself unchanged at the end of the line so `resolve` finds it. `resolve` moves an inline
   thread onto its own lines under the source line, and warns if the hidden words are still missing.
   When the author writes on after the comment's `..` on the same line (`For small $n$ %! is this tight?.., the bound holds.`), the
   batch says so: the words after `..` are the sentence's prose and `resolve` puts them back after the comment's point. Do not
   retype them; to change them, edit them where they are, after the `..`.
3. **Publish.** `$PT push <slug> -m "<what changed>"`. It compiles the affected main file with the project's engine, commits,
   merges with anything typed meanwhile, and publishes. On exit 6, fix the new LaTeX errors it lists; if a note causes one, replace
   that note's line with `%!<id> <comment>` and `%!<id>> <reply>` lines. On exit 7 (a guard), restore what it names, or pass the
   flag only if the comment asked for that change. On exit 3, someone rewrote the same lines while you worked: your diff is saved
   as a patch, the checkout matches the paper again and those comments are back to "sent"; redo them on the new text. If
   `resolve` then says a comment changed, restart the watcher: it sends the new version.
4. **Learn**, following `references/learning.md`: the events listed in the batch (`$PT learn <slug>` shows full diffs) and any
   preference the comments state. Update STYLE.md (or NOTES.md for paper-specific points), `$PT learn <slug> --ack <ids>`, and
   commit the vault if the data home is a git repository. An event that is not the author's writing (another session's push, a
   comment read as an edit): `$PT learn <slug> --discard <ids> --why "<reason>"`, and say if it points to a bug in `pairtex`.
   Both `--ack` and `--discard` work while the watcher runs.
5. **Restart** the watcher the way you started it (step 4 of "Start the loop").
6. **Report** to the author in chat in two to four lines, in the language `preferences.md` asks for (else the author's): the
   comments, what changed, any rule learned, anything that needs them.

## Editing rules

- **Do what the comment asks, at its scope.** "This" means the paragraph the batch names (for an end-of-line comment, that
  sentence). Leave everything else as it is: do not restyle text the comment did not touch.
- **One comment, every parallel place.** If the fix applies to the same term, claim or construction elsewhere (the abstract, the
  introduction, the conclusion), apply it there too and list where in the reply.
- **Never change the science on your own.** Claims, numbers, theorem statements, assumptions and citations change only when the
  comment asks and the project's facts or results support it. Otherwise answer in the reply and leave the text.
- **Write in the author's style.** STYLE.md and the base rules apply to every sentence you write.
- **Keep it compiling and intact.** Keep labels, macros and `\ref` targets. Never touch comment lines or other threads (only
  `pairtex resolve` rewrites them), other loops' notes, the protected note macros, or files the comment is not about. Add no new files
  unless asked.
- **A question gets an answer,** with the evidence (equation, section, result), and an edit when the text should not leave the
  next reader asking the same.
- **A decision that is the author's** (two readings, a structural change, a claim you cannot support): make no edit; reply with
  the options numbered (`Two ways: (1) … (2) …`). The author answers with a follow-up such as `%! 2..`.
- **When a request conflicts with a fact,** do the correct version and say so in the reply.

## Answering a question

The author asks to understand the text: why the current or the previous version is written this way, what a sentence does for
the paper, how two parts relate. Answer from evidence, not from guesses:
- **The paper itself.** Read the whole section, and what the sentence sets up later (grep the terms, `\ref` targets, the results
  it previews). Say concretely what it does: "defines B, which Proposition 3 and Section 5.2 use".
- **Why it was written so.** The batch lists the commits that changed these lines and the closest passage in the earlier drafts
  (`earlier_versions` in `project.json`). Read the diffs (`git -C <checkout> show <sha>`), and the project's own records that
  NOTES.md names (change lists, coordination logs, earlier comments). Name the source of the reason. If no record says why, say so
  and give your reading as a reading.
- **Answer only.** No edit, however tempting. If the answer shows a problem, end with one line offering the fix ("If you want,
  `%! do it..` and I will move it after the definition"); the follow-up then arrives as a change request in the same thread.

## Replies

English unless `preferences.md` says otherwise, one to three short sentences; an answer to a question may take up to five. A reply
is printed in the PDF as part of the note, so it is LaTeX: plain text, maths in `$...$`, `\Cref{...}` for references (it prints
the real number), and only characters the paper's engine prints (`resolve` turns arrows and Greek letters into maths and refuses
the rest). Say what changed and where (section names, not line numbers), quote the new wording when it is short, list the
parallel places, and offer one alternative only if it is worth the author's time. No boilerplate: the author knows to delete the
note to accept.

## Before submission

When the author prepares a version for a journal, a conference or arXiv:
- `$PT check <slug>` lists the notes, open comments, threads, `[[ ]]` brackets, the note macro and the protected coauthor notes
  still in the paper (exit 1 while anything is left).
- Hiding every note at once: the author deletes the first `%` of the `% \def\hideclaudenotes{}` line in the preamble.
- `$PT clean <slug> --out <empty dir> --compile` writes a copy without notes, comments, threads, brackets, the note macro and,
  unless `--keep-comments`, every other `%` comment (arXiv publishes the source). Coauthor notes stay; it says so.

## Stop

When the author says stop (停, 先到这里), stop the background watcher, run `$PT learn <slug>` for a last pass, and say in a few
lines what the style guide gained this session.

## Feedback about the loop

When the author comments on how the loop behaves (speed, replies, what it learns, how it reports), record it in `preferences.md`
in the vault with their words and the rule, and commit the vault. A change to `pairtex` itself also gets a `CHANGELOG.md` entry in the
code repository. Writing-style feedback goes in `STYLE.md` instead.
