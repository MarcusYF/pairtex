# PairLab for coding agents

This file is for coding agents: Claude Code, Codex, and any other agent that can run shell commands and edit files. PairLab
is three tools that share one design. Each has its own `AGENTS.md` with the full steps; this page says which tool fits a
request, how to install one or all of them for the user, and the rules every tool shares.

## Which tool

| The user wants to … | Tool | Its guide |
| --- | --- | --- |
| report what they found, explain a paper or idea, an animated HTML deck, a visual explainer | **PairDeck** | [pairdeck/AGENTS.md](pairdeck/AGENTS.md) |
| write or revise a LaTeX paper with comments in the source (Overleaf, a git remote, a local folder) | **PairTeX** | [pairtex/AGENTS.md](pairtex/AGENTS.md) |
| make or revise a talk: slides with builds, a speaker script, comments from coauthors | **PairTalk** | [pairtalk/AGENTS.md](pairtalk/AGENTS.md) |

## Which agent, which plan

No tool has a model or an API key of its own. Each is a command-line tool plus a skill; the thinking is done by the agent the
user already runs, on the user's own plan: **Claude Code** (a Claude subscription or an Anthropic API key), **Codex** (a
ChatGPT plan or an OpenAI API key), or another agent that runs shell commands (it reads the tool's `skill/SKILL.md`).
`install.sh` links each skill into `~/.claude/skills/<tool>` and `~/.agents/skills/<tool>`, so one install serves both. The
user's style guides and projects live in each tool's data home (`~/.pairdeck`, `~/.pairtex`, `~/.pairtalk`), not in the agent,
so they can switch agents at any time.

## Install for the user

When the user asks you to install PairLab or one of its tools (for example "install PairLab from
https://github.com/MarcusYF/pairlab"):

1. **Get the code.** If you are not in a clone, `git clone https://github.com/MarcusYF/pairlab ~/pairlab`. Another folder only
   if the user names one. To update later: `git -C ~/pairlab pull`.
2. **Ask which tools**, unless the request says: all three, or the ones for their next task. Then run
   `~/pairlab/install.sh` (all) or `~/pairlab/install.sh <tool> …`. Read what it prints: each tool checks what it needs
   (Python 3.9+, git, latexmk, Chrome, Node 22) and says what is missing. Install a missing dependency only if the user says
   yes.
3. **Follow each installed tool's `AGENTS.md`** from its own setup step on: the user's name (once per tool), where their work
   lives, and the offer to **seed** the tool's style guide from two to five things the user made themselves (papers for
   PairTeX, decks for PairDeck, talks and scripts for PairTalk). Seeding is optional and never needed to start.
4. **Tell the user** in a few lines what is installed, how to give feedback in each tool, and what to say to start.

## Rules every tool shares

- **The style vault** (`docs/style-vault.md`): read the tool's `STYLE.md` before every piece of work; after each round, turn the
  evidence into entries, acknowledge it with `<tool> learn --ack`, commit the vault, and name any new rule in your report so the
  user can object. Only the owner's own edits and comments teach their style; a coauthor's never do. Style never changes a
  claim, a number or a result.
- **Credentials are the user's.** Never ask for a token or password in chat, never type one, and never put one in a file, a URL
  or a command. Overleaf tokens, git credentials and Cloudflare logins are stored by the user, in their own terminal.
- **Publish only what the loop was asked for.** Starting a tool's loop at the user's request authorizes publishing the changes
  that answer the feedback it receives, in that project, for this session. Nothing else: no other projects, no force pushes,
  no deletions the user did not ask for.
- **The user's work stays theirs.** Their papers, decks, talks, evidence and style guides stay in the data home and their own
  projects. Never copy them into this repository.
