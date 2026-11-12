#!/bin/sh
# Install PairTalk (macOS or Linux). Safe to rerun; an agent can run it unattended. The suite's ./install.sh pairtalk runs it.
#   - links the skill for Claude Code:  ~/.claude/skills/pairtalk
#   - links the skill for Codex and other agents that read the open agent-skills format:  ~/.agents/skills/pairtalk
#   - links the CLI as ~/.local/bin/pairtalk
#   - checks Python, git, Node and Chrome; nothing is downloaded (the deck tools' packages: npm install, once, here)
# Then create your profile: pairtalk setup --name "Your Name"
set -e
APP="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$APP/bin/pairtalk"
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$dir"
  ln -sfn "$APP/skill" "$dir/pairtalk"
  echo "linked $dir/pairtalk -> $APP/skill"
done
mkdir -p "$HOME/.local/bin"
ln -sfn "$APP/bin/pairtalk" "$HOME/.local/bin/pairtalk"
echo "linked ~/.local/bin/pairtalk -> $APP/bin/pairtalk"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "note: ~/.local/bin is not on your PATH; add it, or call $HOME/.local/bin/pairtalk" ;;
esac
command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' \
  || echo "missing: Python 3.9 or newer (python3)"
command -v git >/dev/null 2>&1 || echo "missing: git"
if command -v node >/dev/null 2>&1 && node -e 'process.exit(+process.versions.node.split(".")[0] < 22 ? 1 : 0)'; then
  [ -d "$APP/node_modules/acorn" ] && [ -d "$APP/node_modules/playwright" ] \
    || echo "next: (cd $APP && npm install)   # the deck tools' packages, acorn and playwright (it downloads no browser)"
else
  echo "missing: Node 22 or newer (https://nodejs.org); then: (cd $APP && npm install)"
fi
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/google-chrome-stable /usr/bin/chromium /usr/bin/chromium-browser; do
  [ -x "$c" ] && CHROME_FOUND=1 && break
done
[ -n "$CHROME_FOUND" ] || [ -n "$CHROME_PATH" ] || echo "note: no Chrome found; screenshots (pairtalk shots) need Chrome or Chromium, or CHROME_PATH"
if "$APP/bin/pairtalk" paths | grep -q "none yet"; then
  echo "next: pairtalk setup --name \"Your Name\""
else
  echo "profile: $("$APP/bin/pairtalk" paths | sed -n 's/^ *profile  //p')"
fi
