# PairPoster for any coding agent

For coding agents: Claude Code, Codex, and any other agent that runs shell commands and edits files.

## Which agent, which plan

`pairposter` has no model and no API key. It is a command-line tool (Python 3.9+, git, Chrome or Chromium) plus a skill; the
thinking is done by the agent the user already runs, on their own plan. The installer links the skill into
`~/.claude/skills/pairposter` (Claude Code) and `~/.agents/skills/pairposter` (Codex and others). The profile, the style
guide and the posters' state live in `~/.pairposter`, so the user can switch agents at any time. PairPoster runs on
PairDeck's code (`../pairdeck`), so the two folders stay together.

## Install for the user

1. **Check the tools:** `python3 --version` (3.9+), `git --version`, Chrome or Chromium. Without Chrome everything works
   except `qa`'s measurements and screenshots and `print`: say so, and install it only if the user says yes.
2. **Get the code:** if not in a clone, `git clone https://github.com/MarcusYF/pairlab ~/pairlab`.
3. **Install:** `~/pairlab/install.sh pairposter`.
4. **Ask, in one message:** the user's name; whether they have past posters (PDF) to start the style guide from; and the
   poster at hand (the paper, a draft, the venue and its size).
5. **Set up:** `pairposter setup --name "…" --agent <your name>`; seed if they gave posters (`skill/references/seeding.md`).
6. **Tell the user** how to ask: "make a poster for this paper", "watch my poster".

## Run it

Follow `skill/SKILL.md`: build (`new`, write, `qa`, look at the screenshots, `snapshot`), show (`review`), loop (`watch` in
the background, `resolve`, `qa`, `snapshot`, `learn`), and print (`print`). Starting the loop at the user's request
authorizes edits to that poster only; printing services, uploads to a venue and sending files need the user's explicit
go-ahead.
