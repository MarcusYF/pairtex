#!/bin/sh
# Install PairPoster (macOS or Linux). Safe to rerun; an agent can run it unattended. The suite's ./install.sh pairposter runs it.
#   - links the skill for Claude Code:  ~/.claude/skills/pairposter
#   - links the skill for Codex and other agents that read the open agent-skills format:  ~/.agents/skills/pairposter
#   - links the CLI as ~/.local/bin/pairposter (it runs on PairDeck's code in ../pairdeck, so keep the folders together)
#   - checks Python and Chrome; nothing is downloaded
# Then create your profile: pairposter setup --name "Your Name"
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
[ -f "$APP/../pairdeck/bin/pairdeck" ] || { echo "missing: $APP/../pairdeck (PairPoster runs on PairDeck's code)"; exit 1; }
chmod +x "$APP/bin/pairposter" "$APP/../pairdeck/bin/pairdeck"
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$dir"
  ln -sfn "$APP/skill" "$dir/pairposter"
  echo "linked $dir/pairposter -> $APP/skill"
done
mkdir -p "$HOME/.local/bin"
ln -sfn "$APP/bin/pairposter" "$HOME/.local/bin/pairposter"
echo "linked ~/.local/bin/pairposter -> $APP/bin/pairposter"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "note: ~/.local/bin is not on your PATH; add it, or call $HOME/.local/bin/pairposter" ;;
esac
command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' \
  || echo "missing: Python 3.9 or newer (python3)"
command -v git >/dev/null 2>&1 || echo "note: git is not installed; the style vault is kept without history until it is"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/google-chrome-stable /usr/bin/chromium /usr/bin/chromium-browser; do
  [ -x "$c" ] && CHROME_FOUND=1 && break
done
[ -n "$CHROME_FOUND" ] || [ -n "$CHROME" ] || echo "note: no Chrome found; checks and printing (pairposter qa, print) need Chrome or Chromium, or CHROME=/path"
if "$APP/bin/pairposter" paths | grep -q "none yet"; then
  echo "next: pairposter setup --name \"Your Name\""
else
  echo "profile: $("$APP/bin/pairposter" paths | sed -n 's/^ *profile  //p')"
fi
