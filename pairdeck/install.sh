#!/bin/sh
# Install PairDeck (macOS or Linux). Safe to rerun; an agent can run it unattended. The suite's ./install.sh pairdeck runs it.
#   - links the skill for Claude Code:  ~/.claude/skills/pairdeck
#   - links the skill for Codex and other agents that read the open agent-skills format:  ~/.agents/skills/pairdeck
#   - links the CLI as ~/.local/bin/pairdeck
#   - checks Python and Chrome; nothing is downloaded
# Then create your profile: pairdeck setup --name "Your Name"
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$APP/bin/pairdeck"
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$dir"
  ln -sfn "$APP/skill" "$dir/pairdeck"
  echo "linked $dir/pairdeck -> $APP/skill"
done
mkdir -p "$HOME/.local/bin"
ln -sfn "$APP/bin/pairdeck" "$HOME/.local/bin/pairdeck"
echo "linked ~/.local/bin/pairdeck -> $APP/bin/pairdeck"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "note: ~/.local/bin is not on your PATH; add it, or call $HOME/.local/bin/pairdeck" ;;
esac
command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' \
  || echo "missing: Python 3.9 or newer (python3)"
command -v git >/dev/null 2>&1 || echo "note: git is not installed; the style vault is kept without history until it is"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/google-chrome-stable /usr/bin/chromium /usr/bin/chromium-browser; do
  [ -x "$c" ] && CHROME_FOUND=1 && break
done
[ -n "$CHROME_FOUND" ] || [ -n "$CHROME" ] || echo "note: no Chrome found; screenshots (pairdeck qa) need Chrome or Chromium, or CHROME=/path"
if "$APP/bin/pairdeck" paths | grep -q "none yet"; then
  echo "next: pairdeck setup --name \"Your Name\""
else
  echo "profile: $("$APP/bin/pairdeck" paths | sed -n 's/^ *profile  //p')"
fi
