# PairTeX for any coding agent

This file is for coding agents: Claude Code, Codex, and any other agent that can run shell commands and edit files. It has
three parts: which agent and subscription to use, how to **install PairTeX for the user** without them typing anything but
their answers, and how to run the loop.

## Which agent, which subscription

`pairtex` has no model and no API key of its own. It is a command-line tool (Python 3.9+, git, latexmk) that turns a LaTeX paper
into a queue of comments. The thinking is done by the agent the user already runs, on the user's own plan:

| Agent | Plan it runs on | Reads the skill from |
| --- | --- | --- |
| Claude Code | a Claude subscription or an Anthropic API key | `~/.claude/skills/pairtex` |
| Codex (CLI, IDE extension, ChatGPT desktop app) | a ChatGPT plan or an OpenAI API key | `~/.agents/skills/pairtex` |
| Another agent that runs shell commands | its own | this file and `skill/SKILL.md` |

`install.sh` links the skill into both folders, so one install serves Claude Code and Codex. The user can switch agents at any
time: the loop's state (profile, style guide, papers) lives in the data home, `~/.pairtex`, not in the agent. Only one session
watches a given paper at a time; `pairtex watch <slug> --takeover` moves it.

The profile's `agent` name is what notes print before the reply ("Claude:", "Codex:"). Set it with `pairtex setup --agent Codex`.
A paper's note macro keeps the name it was created with; a user who switches agents often can choose a neutral name, such as
`--agent AI`. The `Co-Authored-By: Claude` commit trailer is added only for Claude; set `"trailer"` in `profile.json` for another.

## Install PairTeX for the user

When the user asks you to install or set up PairTeX (for example "install PairTeX from https://github.com/MarcusYF/pairtex"),
you may do the whole installation yourself. Follow these steps in order. Ask the user only where a step says so, and keep each
question short.

1. **Check the tools.** `python3 --version` (3.9 or newer), `git --version`, `latexmk -v`. Without Python or git, stop and tell
   the user what to install. Without latexmk, carry on: the compile check is skipped until TeX is installed. Tell the user how to
   install it (macOS: `brew install --cask mactex-no-gui`; Debian or Ubuntu: `sudo apt install latexmk texlive-latex-extra`),
   and install it yourself only if they say yes.
2. **Get the code.** If you are not already in a clone, run `git clone https://github.com/MarcusYF/pairtex ~/pairtex`. Use
   another folder only if the user names one. To update later, run `git -C ~/pairtex pull`.
3. **Install.** Run `~/pairtex/install.sh`. It links the skill for Claude Code and for Codex, and links the CLI at
   `~/.local/bin/pairtex`. If it says `~/.local/bin` is not on the PATH, call `~/.local/bin/pairtex` by its full path, and give
   the user the line for their shell profile. Do not edit the shell profile unless they ask.
4. **Ask two things, in one message:**
   - their name exactly as Overleaf shows it to coauthors (for a git remote, the name on their commits). On a shared paper the
     loop answers only comments written under this name;
   - where the paper lives (an Overleaf project link, a git URL or a local folder), and the main `.tex` file if they know it.

   Then run `pairtex setup --name "<their name>" --agent <your name: Claude, Codex, …>`.
5. **Credentials: the user's job, never yours.**
   - **Overleaf.** The git integration needs a git authentication token. The user creates it in Overleaf (Account settings, Git
     integration), then stores it once by running this in their own terminal:
     `git ls-remote https://git.overleaf.com/<project id>`. The username is `git` and the password is the token. Their
     credential helper keeps it (the macOS keychain, Git Credential Manager, libsecret).
   - **Private git remote.** The user's usual git credentials.
   - **Folder.** Nothing needed.

   Never ask for a token or password in chat, never type one, and never put one in a file, a URL or a command.
6. **Add the paper.** Run `pairtex init <slug> --overleaf <project id> --main <main.tex>`, or `--git <url>`, or `--folder <dir>`.
   - The slug is a short lowercase name taken from the paper's title.
   - The project id is the part after `/project/` in the Overleaf link.
   - If the main file is unknown, leave out `--main`. After init, find the file with `\documentclass` in the checkout that
     `pairtex paths` shows, and record it as `"main"` in `projects/<slug>/project.json`.
   - If init says the clone failed for want of credentials, go back to step 5.
   - Coauthors' note macros (`\ada{…}`) belong in `--protect ada`. Ask about them only if the paper defines such macros.
7. **Check.** `pairtex status <slug>` shows the paper's head and the comments by state.
8. **Tell the user** in three short lines:
   - PairTeX is installed and the paper is added;
   - how to comment: `%! … ..` to ask for a change, `%? … ..` to ask a question, `[[ ]]` around the words meant; `..` sends it;
   - how to start: say "watch <slug>" to you, in this agent or any other where PairTeX is installed.

   Offer to start the loop now.

While installing, do not edit the paper, push anything to it, start the watcher before the user asks, or change git
configuration or shell files without asking. The first push happens only once the loop runs and the user has commented.

## Run the loop

Read `skill/SKILL.md` and follow it; it is the full procedure. Codex and Claude Code load it as the `pairtex` skill. Where it
says to start the watcher "in the background", use what your harness offers:

- **You can run a command in the background and be woken when it exits** (Claude Code): run `pairtex watch <slug>` that way.
- **You can wait on a long foreground command:** run `pairtex watch <slug> --max-hours 0.5` in the foreground. Exit 0 prints
  a batch. Exit 1 means nothing arrived in that time: run it again.
- **Your commands time out after a short while:** poll instead. `pairtex watch <slug> --once` returns at once, with a batch
  (exit 0) or "no comment ready" (exit 1). Poll every 30 to 60 seconds while the author is writing.
- **You stop after each answer and wait for the user:** run one round per prompt. When the user says "check <slug>", run
  `pairtex watch <slug> --once` and handle what it returns.

Everything else is the same for every agent:

1. Edit the paper in `projects/<slug>/repo/`.
2. Run `pairtex resolve <slug> <id> "<reply>"` after each comment.
3. Run `pairtex push <slug> -m "…"`.
4. Learn from the evidence (`skill/references/learning.md`).
5. Watch again.

`pairtex paths` says where the profile, style vault and projects are.
