#!/bin/sh
# Install PairTeX (macOS or Linux). Safe to rerun; an agent can run it unattended.
#   - links the skill for Claude Code:  ~/.claude/skills/pairtex
#   - links the skill for Codex and other agents that read the open agent-skills format:  ~/.agents/skills/pairtex
#   - links the CLI as ~/.local/bin/pairtex (and ~/.local/bin/ow, its old name)
# Then create your profile: pairtex setup --name "Your Name"   (your name as Overleaf shows it to coauthors)
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$APP/bin/pairtex"
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$dir"
  ln -sfn "$APP/skill" "$dir/pairtex"
  echo "linked $dir/pairtex -> $APP/skill"
done
OLD="$HOME/.claude/skills/overleaf-writer"   # the skill's name before 0.4.1
if [ -L "$OLD" ] && [ "$(cd "$OLD" && pwd -P)" = "$(cd "$APP/skill" && pwd -P)" ]; then
  rm "$OLD" && echo "removed the old link ~/.claude/skills/overleaf-writer"
fi
mkdir -p "$HOME/.local/bin"
ln -sfn "$APP/bin/pairtex" "$HOME/.local/bin/pairtex"
ln -sfn "$APP/bin/pairtex" "$HOME/.local/bin/ow"
echo "linked ~/.local/bin/pairtex (and ow) -> $APP/bin/pairtex"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "note: ~/.local/bin is not on your PATH; add it, or call $HOME/.local/bin/pairtex" ;;
esac
command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' \
  || echo "missing: Python 3.9 or newer (python3)"
command -v git >/dev/null 2>&1 || echo "missing: git"
command -v latexmk >/dev/null 2>&1 || echo "note: latexmk is not installed; the compile check is skipped until it is (TeX Live or MacTeX)"
if "$APP/bin/pairtex" paths | grep -q "none yet"; then
  echo "next: pairtex setup --name \"Your Name\""
else
  echo "profile: $("$APP/bin/pairtex" paths | sed -n 's/^ *profile  //p')"
fi
