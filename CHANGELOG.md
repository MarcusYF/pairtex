# Changelog

PairLab's releases. Each tool keeps its own detailed changelog: [PairDeck](pairdeck/CHANGELOG.md),
[PairTeX](pairtex/CHANGELOG.md), [PairTalk](pairtalk/CHANGELOG.md).

## Unreleased

- **PairPoster 0.1.0** (new): conference posters as one HTML page at the venue's size, built picture-first (icon chains,
  charts, big numbers, formula boxes) with word budgets per block; `qa` measures overflow, type size at print scale, words
  and image resolution and shoots close-ups; `print` writes the one-page vector PDF and the venue's PNG; the comment loop,
  snapshots and style learning are PairDeck's, run in a poster flavour, with a poster style vault in `~/.pairposter`.
- **PairDeck 0.1.1**: the same program now also runs as PairPoster; the review overlay takes its wording and anchors from
  the tool and records the labelled block a comment points at.
- `./install.sh` installs all four tools.

## 0.1.0 (2026-11-12)

PairTeX becomes one of three tools, and its repository becomes PairLab's.
- **PairDeck 0.1.0** (new): animated HTML decks that report a finding or explain an idea, with a local review page where the
  author comments on a slide, and a visual style guide seeded from the author's own decks.
- **PairTeX 0.5.0**: `pairtex seed` starts the writing-style guide from the author's own papers.
- **PairTalk 0.1.0** (new): talks with builds and a speaker script; coauthors comment on a slide or edit the script on an
  optional shared site or in a local inbox, and a talk style guide is seeded from the author's own slides and scripts.
  Built on [html-slide](https://github.com/Yanwei-Sun/html-slide) by Yanwei Sun.
- **One contract** for the three style vaults ([docs/style-vault.md](docs/style-vault.md)): the same data-home layout,
  evidence kinds, `seed`, `learn`, `watch` and `resolve` in every tool.
- **One installer**: `./install.sh` installs all three, `./install.sh <tool>` one. PairTeX moved to `pairtex/`; `skill` and
  `bin/pairtex` at the top level keep installs from before the move working, and `pairtex/install.sh` (or `./install.sh
  pairtex`) updates their links.
