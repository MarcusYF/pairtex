#!/bin/sh
# Install PairLab's tools (macOS or Linux). Safe to rerun; an agent can run it unattended.
#   ./install.sh                     all four: PairDeck, PairTeX, PairTalk, PairPoster
#   ./install.sh pairtex             one or more by name: pairdeck pairtex pairtalk pairposter
# Each tool's own install.sh links its skill for Claude Code (~/.claude/skills/<tool>) and for Codex and other agents
# that read the open agent-skills format (~/.agents/skills/<tool>), links its command in ~/.local/bin, and checks what
# it needs. Nothing is downloaded and nothing outside those folders changes.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS="${*:-pairdeck pairtex pairtalk pairposter}"
for tool in $TOOLS; do
  case "$tool" in
    pairdeck|pairtex|pairtalk|pairposter) ;;
    *) echo "unknown tool: $tool (choose from pairdeck, pairtex, pairtalk, pairposter)"; exit 2 ;;
  esac
done
for tool in $TOOLS; do
  echo "== $tool"
  sh "$ROOT/$tool/install.sh"
done
echo "== done. Next, per tool: <tool> setup --name \"Your Name\", then optionally <tool> seed <your past work>."
