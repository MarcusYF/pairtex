# PairDeck for any coding agent

This file is for coding agents: Claude Code, Codex, and any other agent that can run shell commands and edit files. It has
three parts: which agent and subscription to use, how to **install PairDeck for the user** without them typing anything but
their answers, and how to run the comment loop.

## Which agent, which subscription

`pairdeck` has no model and no API key of its own. It is a command-line tool (Python 3.9+, git, and Chrome or Chromium for
screenshots) plus a skill. The thinking (the story, the pictures, the fixes, the style guide) is done by the agent the user
already runs, on the user's own plan:

| Agent | Plan it runs on | Reads the skill from |
| --- | --- | --- |
| Claude Code | a Claude subscription or an Anthropic API key | `~/.claude/skills/pairdeck` |
| Codex (CLI, IDE extension, desktop app) | a ChatGPT plan or an OpenAI API key | `~/.agents/skills/pairdeck` |
| Another agent that runs shell commands | its own | this file and `skill/SKILL.md` |

The installer links the skill into both folders, so one install serves Claude Code and Codex. The user can switch agents at
any time: the profile, the style guide and the decks' state live in the data home, `~/.pairdeck`, not in the agent. Only one
session watches a given deck at a time; `pairdeck watch <slug> --takeover` moves it. The profile's `agent` name is what replies
show ("Claude:", "Codex:"); set it with `pairdeck setup --agent Codex`.

## Install PairDeck for the user

When the user asks you to install or set up PairDeck, you may do the whole installation yourself. Follow these steps in order.
Ask the user only where a step says so, and keep each question short.

1. **Check the tools.** `python3 --version` (3.9 or newer), `git --version`, and Chrome or Chromium (macOS:
   `/Applications/Google Chrome.app`; Linux: `google-chrome` or `chromium` on the PATH). Without Python or git, stop and tell
   the user what to install. Without Chrome, carry on: everything works except the screenshots of `pairdeck qa` and
   `pairdeck card`; tell the user, and install it only if they say yes.
2. **Get the code.** If you are not already in a clone, run `git clone https://github.com/MarcusYF/pairlab ~/pairlab`. Use
   another folder only if the user names one. To update later: `git -C ~/pairlab pull`.
3. **Install.** Run `~/pairlab/install.sh pairdeck`. It links the skill for Claude Code and Codex and the CLI at
   `~/.local/bin/pairdeck`. If `~/.local/bin` is not on the PATH, call `~/.local/bin/pairdeck` by its full path and give the
   user the line for their shell profile. Do not edit the shell profile unless they ask.
4. **Ask two things, in one message:**
   - their name (the review page shows it on their comments);
   - whether they have past decks to start the style guide from (folders or files: `.pptx`, `.pdf` exports, `.html` decks;
     Keynote files exported to PDF first), and which of them they made mostly themselves.

   Then run `pairdeck setup --name "<their name>" --agent <your name: Claude, Codex, …>`.
5. **Seed, if they gave decks:** `pairdeck seed <paths> --note "<what they are>"`, then follow `skill/references/seeding.md`:
   look at the page images and stats, draft `STYLE.md` entries, and show the user the five to ten strongest to keep, edit or
   delete. Seeding reads only the files the user named and writes only into the data home.
6. **Check.** `pairdeck status` shows the data home, the style guide and the seeds.
7. **Tell the user** in three short lines:
   - PairDeck is installed (and what the style guide learned from their decks, if seeded);
   - how to start: "make a visual explainer of <material> with pairdeck", in this agent or any other where it is installed;
   - how to comment: on the review page, press Comment, drag a box over the slide, type, Send.

While installing, do not create a deck, start a server or the watcher, or change git configuration or shell files without
asking.

## Run the loop

Read `skill/SKILL.md` and follow it; it is the full procedure (build, check, snapshot, review, watch, resolve, learn). Codex and
Claude Code load it as the `pairdeck` skill. Two commands run for a long time:

- `pairdeck review <slug>` serves the review page until stopped. Run it in the background (Claude Code: `run_in_background`;
  elsewhere `nohup pairdeck review <slug> >/dev/null 2>&1 &`), and give the user the URL it prints (`pairdeck status <slug>`
  shows it again).
- `pairdeck watch <slug>` waits for feedback and exits with one batch. Use what your harness offers:
  - **You can run a command in the background and be woken when it exits** (Claude Code): run it that way.
  - **You can wait on a long foreground command:** `pairdeck watch <slug> --max-hours 0.5`. Exit 0 prints a batch; exit 1
    means nothing arrived in that time: run it again.
  - **Your commands time out after a short while:** poll. `pairdeck watch <slug> --once` returns at once, with a batch (exit 0)
    or "nothing ready" (exit 1). Poll every 30 to 60 seconds while the user is reviewing.
  - **You stop after each answer and wait for the user:** when the user says "check my deck", run `pairdeck watch <slug> --once`
    and handle what it returns.

For every batch, the same steps for every agent:

1. Edit the deck (its folder is in the batch).
2. `pairdeck resolve <slug> <id> "<reply>"` after each comment.
3. `pairdeck qa <slug> --slides N,M` and look at the screenshots.
4. `pairdeck snapshot <slug>` before watching again (the watcher refuses to start, exit 4, if you forget).
5. Learn from the evidence (`skill/references/learning.md`), `pairdeck learn --ack <ids>`, commit the vault.
6. Watch again.

`pairdeck paths` says where the profile, style vault and decks are.
