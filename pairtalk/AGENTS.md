# PairTalk for any coding agent

This file is for coding agents: Claude Code, Codex, and any other agent that can run shell commands and edit files. It has
three parts: which agent and plan to use, how to **install PairTalk for the user** without them typing anything but their
answers, and how to run the loop.

## Which agent, which plan

`pairtalk` has no model and no API key of its own. It is a command-line tool (Python 3.9+, git, Node 22+, Chrome for
screenshots) that turns a talk folder into slides you can review and a queue of comments and script edits. The thinking is done
by the agent the user already runs, on the user's own plan:

| Agent | Plan it runs on | Reads the skill from |
| --- | --- | --- |
| Claude Code | a Claude subscription or an Anthropic API key | `~/.claude/skills/pairtalk` |
| Codex (CLI, IDE extension, desktop app) | a ChatGPT plan or an OpenAI API key | `~/.agents/skills/pairtalk` |
| Another agent that runs shell commands | its own | this file and `skill/SKILL.md` |

The installer links the skill into both folders, so one install serves Claude Code and Codex. The user can switch agents at any
time: the talks' settings, the inbox and the style guide live in the data home, `~/.pairtalk`, not in the agent. Only one
session watches a given talk at a time; `pairtalk watch <talk> --takeover` moves it.

## Install PairTalk for the user

When the user asks you to install PairTalk (for example "install PairTalk from https://github.com/MarcusYF/pairlab"), you may
do the whole installation yourself. Follow these steps in order. Ask the user only where a step says so.

1. **Check the tools.** `python3 --version` (3.9 or newer), `git --version`, `node --version` (22 or newer). Without Python,
   git or Node, stop and tell the user what to install. Chrome or Chromium is needed only for screenshots; say so if it is
   missing.
2. **Get the code.** If you are not already in a clone, run `git clone https://github.com/MarcusYF/pairlab ~/pairlab`. Use
   another folder only if the user names one. To update later, `git -C ~/pairlab pull`.
3. **Install.** Run `~/pairlab/install.sh pairtalk` (or `~/pairlab/pairtalk/install.sh`). It links the skill for Claude Code
   and Codex and links the CLI at `~/.local/bin/pairtalk`. Then run `npm install` once in `~/pairlab/pairtalk` (acorn and
   Playwright from npm; no browser is downloaded). If the installer says
   `~/.local/bin` is not on the PATH, call `~/.local/bin/pairtalk` by its full path, and give the user the line for their shell
   profile. Do not edit the shell profile unless they ask.
4. **Ask two things, in one message:** their name as coauthors see it on comments (only comments and edits under this name
   teach their style guide), and whether they have a talk to start (its title, slot in minutes, and the paper or results it
   presents) or want to try the demo first. Then run `pairtalk setup --name "<their name>" --agent <your name>`.
5. **Make the talk.** `pairtalk new <talk> --title "<title>" --minutes <slot> --dir <folder>` (the folder where they keep talks;
   by default `./<talk>`), or `pairtalk new demo --example pagerank` for the demo. The talk name is short and lowercase.
6. **Past talks (optional).** If they want the first draft to start from their own style, ask for a few past talks they gave
   alone (`.pptx` with notes, `.pdf`, scripts) and their lengths, and run `pairtalk seed <files> --duration <minutes>` per talk.
   Then follow `skill/references/seeding.md`.
7. **Check.** `pairtalk status <talk>` shows the folder, the inbox and the snapshot.
8. **Tell the user** in three short lines: PairTalk is installed and the talk is made; `pairtalk serve <talk>` shows it in the
   browser (`c` to comment on a slide and click, `s` `s` to edit the script, `v` for the speaker view); say "watch <talk>" to
   you, in this agent or any other where PairTalk is installed. Offer to draft the talk or start the loop now.

While installing, do not write slides, start the watcher, or set up the shared site before the user asks. The shared site needs
the user's own Cloudflare account: follow `skill/references/cloudflare.md`, and never ask for, type or store their passcode,
cookie secret or tokens; Wrangler asks the user for them.

## Run the loop

Read `skill/SKILL.md` and follow it; it is the full procedure. Codex and Claude Code load it as the `pairtalk` skill. Where it
says to start the watcher "in the background", use what your harness offers:

- **You can run a command in the background and be woken when it exits** (Claude Code): run `pairtalk watch <talk>` that way.
- **You can wait on a long foreground command:** run `pairtalk watch <talk> --max-hours 0.5`. Exit 0 prints a batch; exit 1
  means nothing arrived in that time: run it again.
- **Your commands time out after a short while:** poll instead. `pairtalk watch <talk> --once` returns at once, with a batch
  (exit 0) or "nothing new" (exit 1). Poll every 30 to 60 seconds while the author reviews.
- **You stop after each answer and wait for the user:** run one round per prompt. When the user says "check <talk>", run
  `pairtalk watch <talk> --once` and handle what it returns.

Everything else is the same for every agent: fix the slides in the talk folder, `pairtalk script apply`, check with
`pairtalk shots`, `pairtalk snapshot`, `pairtalk resolve` each comment, learn (`skill/references/learning.md`), watch again.
Add `--remote` to `watch`, `script apply` and `resolve` for the shared site, and `pairtalk publish` before replying.
`pairtalk paths` says where everything is.
