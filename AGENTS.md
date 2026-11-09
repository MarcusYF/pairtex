# PairTeX for any coding agent

`bin/pairtex` needs no particular agent. It is a command-line tool (Python 3.9+, git, latexmk) that turns a LaTeX paper into a queue of
comments; any agent that can run shell commands and edit files can run the loop. Claude Code users get the same instructions as a
skill (`skill/SKILL.md`, linked by `install.sh`). This file is for other agents, such as Codex.

## Instructions for the agent

Read `skill/SKILL.md` and follow it; it is the full procedure. Where it says to start the watcher "in the background", use what
your harness offers:

- **The agent can run a command in the background and be woken when it exits** (Claude Code): run `pairtex watch <slug>` that way.
- **The agent can wait on a long foreground command:** run `pairtex watch <slug> --max-hours 0.5` in the foreground. Exit 0 prints
  a batch; exit 1 means nothing arrived in that time: run it again.
- **The agent's commands time out after a short while:** poll instead: `pairtex watch <slug> --once` returns at once, with a batch
  (exit 0) or "no comment ready" (exit 1). Poll every 30 to 60 seconds while the author is writing.

Everything else is the same for every agent: edit `projects/<slug>/repo/`, `pairtex resolve <slug> <id> "<reply>"` after each comment,
`pairtex push <slug> -m "…"`, then learn from the evidence (`skill/references/learning.md`) and watch again. `pairtex paths` says where the
profile, style vault and projects are.

## Setup

```sh
./install.sh                              # links ~/.local/bin/pairtex (and the Claude Code skill)
pairtex setup --name "Ada Lovelace" --agent Codex
```

`--agent` sets the name the notes print before the replies ("Codex:"). The commit trailer that Claude Code adds is left out for
other agents; set `"trailer"` in `profile.json` to add your own.
