# Changelog

## 0.4.2 (2026-11-09)

Fixes from the first days of use on a shared paper.
- **A mid-line comment ends at its first `..`.** Words written after it on the same line (`… %! is this tight?.., the bound
  holds.`) are the sentence's prose: the batch says so, and `resolve` puts them back after the comment's point unless the edit
  already has them. Before, such a comment never became ready. `...` and `../` still do not end a comment.
- **Notes quote the words the author bracketed**, as they were in the batch, not as the edit left them, in TeX quotes
  (``…''), with `~` ties kept. Straight double quotes in a comment or reply become TeX quotes, and a `~` before a command
  (`Prop.~\ref{…}`) stays a tie.
- **Evidence keeps its direction.** The author's edit counts as a revision of the agent's text only if that text was in the file
  when the edit began. Before, an edit made shortly before an agent push from chat (no comment) was matched against the later
  text and stored backwards, as the author changing the agent's text.
- **`learn --ack` works while the watcher runs.** Acknowledged events are flagged in `evidence.jsonl`, as discarded ones already
  were, and leave every batch at once; the watcher drops them from its queue at its next batch.
- `pairtex resolve -h` no longer crashes (a bare `%` in a help string).

## 0.4.1 (2026-11-08)

Named PairTeX, under the MIT license. The name leaves out "Overleaf": the tool also works with any git remote or a local folder,
and it is not an Overleaf product.
- The command is `pairtex` (`bin/pairtex`); `bin/ow`, its old name, stays as a link. The skill is `pairtex`; `install.sh`
  links it at `~/.claude/skills/pairtex`, links `~/.local/bin/pairtex` and `ow`, and removes the old skill link.
- The data home is `~/.pairtex` (`$PAIRTEX_HOME`); `~/.overleaf-writer` and `$OW_HOME` keep working.
- The loop's commits are titled `pairtex: …` and the note block opens with `% PairTeX:`; the old `overleaf-writer:` names are
  still recognised. Evidence calls the author's rewrite `diff_author` (older evidence with `diff_fan` still reads).
- Protected note macros count as text, not maths, when a comment that mentions one becomes a note.

## 0.4.0 (2026-11-08)

Shareable: nothing ties the tool to one person, one machine or one backend any more (`ROADMAP.md`). An install from before 0.4
keeps working unchanged until `migrate`.
- **Profile and data home.** `setup --name …` writes `profile.json` (name, the handle notes print, comment-id prefix, agent
  name) in the data home, with the style vault in `vault/` started from `templates/` and the projects in `projects/`; the data
  home is a git repository. `paths` prints where everything is. `migrate` moves `style/` and `projects/` out of the code folder;
  it refuses while a watcher runs or a comment is half answered.
- **Comments and evidence by author.** A comment's author is the author of the commit that added its marker (Overleaf names the
  editor on each commit). A loop answers its owner's comments and those of the coauthors in `comments_from`; others are left to
  their authors (`status` lists them). Comment ids carry the loop's prefix (`grace3`); other loops' threads are recognised
  (`coauthor_prefixes`, filled by `init` from the notes in the paper). Runs of edits split by author, so only the owner's edits
  and closed threads are evidence; a rewrite after which someone else also edited the file reads "changed by others". `status`
  warns when a coauthor in `comments_from` runs a loop of their own.
- **Notes name the commenter.** `\claude[Handle]{id}{comment}{reply}`, with the owner as default handle, and a switch line
  `% \def\hideclaudenotes{}` that hides every note. A paper with the 0.3 macro keeps it until a note needs another name; then
  the macro is upgraded in place and the old notes print as before.
- **Backends.** `init --git URL` (any git remote; the author's own commits are their edits) and `init --folder DIR` (a local
  folder: snapshots as "Update in editor." commits; a push writes back only files the author has not saved again since, else
  merges with the newer save first).
- **The project's engine.** `"compiler"` in project.json, else a `% !TEX program = …` line in the main file, else `$pdf_mode` in
  `latexmkrc`, else pdfLaTeX. Under XeLaTeX or LuaLaTeX with ctex, xeCJK or luatexja, CJK comments and replies go in the note.
  The compile check reports the page count.
- **Before submission.** `check` lists the notes, comments, threads, brackets, note macro and coauthor notes left in the main
  file and the files it includes (`--all`: every .tex file); exit 1 while any are. `clean --out DIR [--compile]
  [--keep-comments]` writes a copy without them and without `%` comments.
- **Docs.** A README for newcomers, the skill and its learning notes written for any author, `AGENTS.md` for other agents,
  `templates/`, `install.sh` also links the command. `ROADMAP.md`: the plan for 0.4 to 0.6.
- Test: 136 checks against local stand-ins for Overleaf, a git remote and a folder.

## 0.3 (2026-11-07)

- Handled comments become one green note in the PDF where they were written, `\claude{cN}{comment}{reply}`, until the commenter
  deletes it. The comment and the reply are made LaTeX-safe; bare maths such as `a_t=P\mu_t` is set as maths; text the engine
  cannot print stays in a `%` line above the note. Where a note would break the build (maths, tables, macro arguments, the
  preamble), the thread stays in `%` lines.
- `..` ends a comment, so it can take as long as the author likes and run over several lines; `...` is an ellipsis.
- The compile check blocks only new LaTeX errors, and caught a note that would have broken the build in the first real use.

## 0.2 (2026-11-07)

- `%!` asks for a change and `%?` asks a question, answered without touching the text (`resolve` refuses an edit). `%@` still
  works.
- `[[ … ]]` (or `【 … 】`) marks the part of a paragraph a comment is about, across lines too.
- Questions come with the history of their lines and the closest passage in the project's earlier drafts.
- Comments typed in the middle of a sentence: the batch shows which words the comment hid, and `resolve` checks they are back.

## 0.1 (2026-11-07)

First version: a comment loop between an Overleaf project, through its git bridge, and a coding agent, plus a writing-style
guide learned from the edits the author keeps, rewrites and undoes. `init`, `watch`, `resolve`, `push`, `learn`, `show`,
`status`; push with a compile check, guards for coauthor notes and threads, a merge with the author's concurrent typing, and
patch-and-redo on a real conflict. Only the author's own web edits count as style evidence.
