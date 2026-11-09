#!/bin/sh
# Install PairTeX for Claude Code (macOS or Linux). Safe to rerun.
#   - links the skill into ~/.claude/skills/pairtex
#   - links the CLI as ~/.local/bin/pairtex (and ~/.local/bin/ow, its old name)
# Then create your profile: pairtex setup --name "Your Name"   (your name as Overleaf shows it to coauthors)
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$APP/bin/pairtex"
mkdir -p "$HOME/.claude/skills"
ln -sfn "$APP/skill" "$HOME/.claude/skills/pairtex"
echo "linked ~/.claude/skills/pairtex -> $APP/skill"
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
  *) echo "note: add ~/.local/bin to your PATH to type 'pairtex' directly" ;;
esac
for tool in git python3 latexmk; do
  command -v "$tool" >/dev/null 2>&1 || echo "note: $tool is not installed (latexmk is needed only for the compile check)"
done
if "$APP/bin/pairtex" paths | grep -q "none yet"; then
  echo "next: pairtex setup --name \"Your Name\""
else
  echo "profile: $("$APP/bin/pairtex" paths | sed -n 's/^ *profile  //p')"
fi
