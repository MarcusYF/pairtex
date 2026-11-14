<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/figures/banner-dark.svg">
    <img src="docs/figures/banner.svg" width="100%" alt="PairLab: work with your AI agent, interactively, in a style that adapts to yours.">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-27709C" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/tools-PairDeck%20%C2%B7%20PairTeX%20%C2%B7%20PairTalk%20%C2%B7%20PairPoster-C6952C" alt="four tools: PairDeck, PairTeX, PairTalk, PairPoster">
  <img src="https://img.shields.io/badge/runs%20in-Claude%20Code%20%C2%B7%20Codex-6D5398" alt="runs in Claude Code or Codex">
  <img src="https://img.shields.io/badge/no-API%20key-227828" alt="no API key">
</p>

<!-- TABBAR -->
<p align="center"><a href="README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/figures/tab-overview-on-dark.svg"><img src="docs/figures/tab-overview-on.svg" width="176" alt="PairLab: the suite"></picture></a><a href="pairdeck/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/figures/tab-pairdeck-off-dark.svg"><img src="docs/figures/tab-pairdeck-off.svg" width="176" alt="PairDeck: report"></picture></a><a href="pairtex/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/figures/tab-pairtex-off-dark.svg"><img src="docs/figures/tab-pairtex-off.svg" width="176" alt="PairTeX: write"></picture></a><a href="pairtalk/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/figures/tab-pairtalk-off-dark.svg"><img src="docs/figures/tab-pairtalk-off.svg" width="176" alt="PairTalk: present"></picture></a><a href="pairposter/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/figures/tab-pairposter-off-dark.svg"><img src="docs/figures/tab-pairposter-off.svg" width="176" alt="PairPoster: pitch"></picture></a></p>
<!-- /TABBAR -->

PairLab is four research tools built on two ideas. **You work with your AI agent interactively**, on the real thing: you
comment on the slide, in the LaTeX source, on the talk or the poster, and the agent fixes it in the background and replies
next to your comment. **It adapts to your style**: every edit you keep, rewrite or undo teaches it how you write, design and
present, so each round needs fewer comments than the last.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/figures/promises-dark.svg">
    <img src="docs/figures/promises.svg" width="100%" alt="Two ideas behind every PairLab tool. 1. Work with your agent, interactively: you comment where the work is (the slide, the LaTeX source, the talk, the poster); your agent picks it up in the background, fixes it and replies next to your comment; you keep the change, follow up, or edit it yourself. 2. It adapts to your style: every edit you keep, rewrite or undo, and every always or never you say, is evidence; it becomes a style guide of your voice, visual taste and pacing, seeded from your past work, in plain text you can edit.">
  </picture>
</p>

## Interactive: you and your agent, on the same work

- **Comment where the work is.** Drag a box on a slide or a poster, write `%! tighten this..` in your LaTeX source, or leave a
  note on a talk's slide. No copying text into a chat window and back.
- **Your agent answers in place.** A watcher wakes your agent when you comment; it fixes the work, checks it (screenshots,
  print size, a LaTeX build), replies next to your comment, and waits for the next one. A round takes about a minute.
- **You stay in charge.** Press **Keep**, **Follow up**, or edit the thing yourself: your own edits are read as yours and
  kept. Coauthors can comment too; their comments are answered, not learned from.
- **On the agent you already use.** Claude Code or Codex does the thinking, on your own plan. There is no PairLab server,
  model or API key.

## Adaptive: it learns your style

- **Every edit is evidence.** What you keep, rewrite or undo, and every "always" or "never" you write, goes into a style
  guide, `STYLE.md`, one per tool: your academic voice for papers, your visual taste for decks and posters, your pacing and
  phrasing for talks.
- **Rules, with their reasons.** A pattern becomes a rule after three independent pieces of evidence, or at once when you
  state it; each rule lists the edits behind it, and the agent reads the guide before every piece of work.
- **It starts from your own work.** `seed` reads papers, decks, talks and posters you already made, so the first draft is
  already close.
- **Yours to read and edit.** Plain text in a git repository in your home folder; your edits to the guide win.

The tools follow one contract for this memory: [docs/style-vault.md](docs/style-vault.md).

## Four tools, one for each moment

After a brainstorm you report what you found; then you write the paper, give the talk, and pitch the work on a poster.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/figures/workflow-dark.svg">
    <img src="docs/figures/workflow.svg" width="100%" alt="Four moments of research, four tools. PairDeck reports what you found: you comment on a slide in your browser, and your agent delivers an animated HTML deck that explains one idea. PairTeX writes the paper: you write %! comments in your LaTeX source, and your agent edits the paper on Overleaf, git or a folder. PairTalk gives the talk: you and your coauthors comment on the talk site or edit the script, and your agent delivers a talk with builds and a speaker script. PairPoster pitches the work on a poster: you draw boxes on the poster in your browser, and your agent delivers a print-ready poster, the PDF and the PNG. Under all four, your style vault, one per tool, seeded from your own papers, decks, talks and posters, grows with every edit you keep, rewrite or undo, and is read before every piece of work. Your agent does the thinking: Claude Code, Codex, or any agent that runs shell commands, on your own plan.">
  </picture>
</p>


### PairDeck: report what you found

You give your agent the material (a paper, a project, the results of an investigation) and it builds a short web deck that
explains one idea with pictures that build up step by step, checked slide by slide on screenshots. Then you drag a box over
any slide in the local review page and type what should change: the agent fixes the deck in the background and replies under
your comment. Your decks look like yours from the first one, because the style guide is seeded from decks you already made.

<p align="center"><img src="pairdeck/docs/img/review-thread.png" width="100%" alt="The PairDeck review page on the example Simpson's paradox deck: two comments marked with boxes on the slide, and in the side panel the agent's reply 'Both charts now share one scale', with Keep and Follow up buttons."></p>

**[Read the PairDeck page →](pairdeck/README.md)**

### PairTeX: write the paper

You type a comment into the LaTeX source, right where the text is (`%! make this tighter..`). About a minute later the agent
has edited the text, put its reply in a green note next to your comment, and published both back to the same paper:
Overleaf, any git remote, or a folder your editor saves into. Coauthors keep their own loops and their own style guides.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="pairtex/docs/figures/loop-dark.svg">
    <img src="pairtex/docs/figures/loop.svg" width="100%" alt="The PairTeX loop: you comment in your editor; your agent with pairtex picks up the comment, reads the text and your style, edits the .tex and replies; the edit and a green note land in the paper; what you keep, rewrite or undo feeds your style guide.">
  </picture>
</p>

**[Read the PairTeX page →](pairtex/README.md)**

### PairTalk: give the talk

Your talk runs in the browser, one file per slide, with builds click by click and a speaker script, one note per click.
You, or a coauthor through your own passcode-protected site, press `c` on any slide and click, draw a box around the part
you mean, and write. Your agent fixes the slide and the script, checks every click with screenshots, and replies under the
comment. Only your own comments and script rewrites teach your talk style; your coauthors' get fixed and answered.

<p align="center"><img src="pairtalk/docs/img/comment.png" width="100%" alt="A comment on slide 8, click 2 of the example PageRank talk, with its marked box drawn over the chart's guarantee line and the agent's reply under it."></p>

**[Read the PairTalk page →](pairtalk/README.md)**

### PairPoster: pitch it on a poster

A poster is an advertisement for the paper, read standing, in a few seconds. Your agent turns the paper (or your LaTeX poster
draft) into one web page at the venue's exact size, picture first: a schematic instead of a paragraph, phrases instead of
sentences, charts redrawn from the paper's own figure data. It checks what a poster session will see (anything that spills,
type too small at print size, blocks over their word budget), then you zoom in on the review page, drag a box and type. It
prints the one-page vector PDF for the print shop and the PNG the venue's site asks for.

<p align="center"><img src="pairposter/docs/img/review-thread.png" width="100%" alt="The PairPoster review page on the example poster about Simpson's paradox: a comment box over the block that shows which patients got which treatment, and in the side panel the comment and the agent's reply, with Keep and Follow up buttons."></p>

**[Read the PairPoster page →](pairposter/README.md)**

## Why not just a chatbot?

| | A chat window | PairLab |
| --- | --- | --- |
| **Where feedback goes** | You copy the text or slide out, and paste the answer back | Where the work is: the `.tex` source, the slide, the script |
| **What it remembers** | Nothing between sessions; the same correction, again | A style guide per tool, with the evidence behind each rule |
| **How it starts** | A generic voice and a generic look | Your voice and look, seeded from your own papers, decks and talks |
| **What your coauthors see** | Nothing, until you paste it in | Every change as a commit or a new version, with a reply next to the comment |
| **What it costs** | Another subscription or API bill | Nothing extra: the agent you already use, on your plan |

## Install

**Let your agent install it.** Paste this into Claude Code or Codex:

```text
Install PairLab from https://github.com/MarcusYF/pairlab and follow its AGENTS.md
```

It asks which tools you want, installs them, asks your name, and offers to seed each style guide from your own work. You
store credentials (an Overleaf token, a Cloudflare login) yourself, once, in your own terminal: the agent never sees them.

**Or yourself:**

```sh
git clone https://github.com/MarcusYF/pairlab && cd pairlab
./install.sh                          # all four tools, or one: ./install.sh pairtex
pairtex setup --name "Ada Lovelace"
pairtex seed ~/papers/a ~/papers/b.pdf   # optional: your style, from your papers
```

Then, in Claude Code or Codex, say what you want: *"watch mypaper"*, *"make a deck that explains this result"*, *"draft my
talk from these slides"*, *"make a 140 × 90 cm poster for this paper"*. Each tool's page has its three-step start.

| Tool | Needs | Feedback lives in | Data home |
| --- | --- | --- | --- |
| PairDeck | Python 3.9+, Chrome or Chromium | a local review page in your browser | `~/.pairdeck` |
| PairTeX | Python 3.9+, git, latexmk | your LaTeX source (Overleaf, git, a folder) | `~/.pairtex` |
| PairTalk | Node 22+, Python 3.9+, Chrome; Cloudflare optional | a local inbox, or a shared site for coauthors | `~/.pairtalk` |
| PairPoster | Python 3.9+, Chrome | a local review page in your browser | `~/.pairposter` |

All four run on macOS and Linux (Windows: WSL).

## Your data stays yours

The tools talk only to the places you publish to (Overleaf, your git remote, your own Cloudflare site). Your papers, decks,
talks, posters, the evidence and the style guides stay in the data homes on your computer, each a git repository you can read, edit
and revert. Your agent reads the files it works on and sends them to its model provider, as any coding agent does.

## Repository

| Path | What it is |
| --- | --- |
| [`pairdeck/`](pairdeck/README.md) | PairDeck: the `pairdeck` command, its skill, the deck engine, an example deck, tests |
| [`pairtex/`](pairtex/README.md) | PairTeX: the `pairtex` command, its skill, templates, tests |
| [`pairtalk/`](pairtalk/README.md) | PairTalk: the `pairtalk` command, its skill, the talk engine, the optional shared site, an example talk, tests |
| [`pairposter/`](pairposter/README.md) | PairPoster: the `pairposter` command (PairDeck's program in its poster flavour), its skill, the poster engine, `tools/figdata.py`, an example poster, tests |
| [`shared/`](shared/) | Code two tools share: reading slides and decks for `seed` |
| [`docs/style-vault.md`](docs/style-vault.md) | The contract the style vaults follow |
| `install.sh`, [`AGENTS.md`](AGENTS.md) | Install one tool or all; how agents install and run them |
| `bin/`, `skill` | Links to each tool's command, and PairTeX's skill where installs from before 0.5 expect it |
| [`CHANGELOG.md`](CHANGELOG.md) | Releases of the suite; each tool has its own changelog |

## Status

PairTeX 0.5 is in daily use on papers in progress, written on Overleaf with coauthors. PairDeck and PairTalk 0.1 are first
public releases of tools built for the author's own research reports and conference talks; PairPoster 0.1 was built while
polishing a conference poster with them. Issues and pull requests are
welcome.

## Acknowledgments

PairTalk is built on [html-slide](https://github.com/Yanwei-Sun/html-slide) by **Yanwei Sun**, an HTML slide template for
research talks whose comments a coding agent can act on; its slide engine, comment panel and review site started there
([pairtalk/NOTICE.md](pairtalk/NOTICE.md)). PairDeck's and PairTalk's slides use the Computer Modern fonts (SIL Open Font
License) and MathJax (Apache 2.0); PairPoster's posters use Nunito (SIL Open Font License) and MathJax.

## License

MIT ([LICENSE](LICENSE)), except PairTalk's code derived from html-slide, which keeps html-slide's own permissive notice
([pairtalk/NOTICE.md](pairtalk/NOTICE.md)). PairLab is an independent project, not affiliated with Overleaf, Anthropic, OpenAI or Cloudflare.
