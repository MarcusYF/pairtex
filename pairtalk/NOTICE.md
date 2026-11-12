# Notice: html-slide by Yanwei Sun

PairTalk is built on **[html-slide](https://github.com/Yanwei-Sun/html-slide)** by **Yanwei Sun**, an HTML slide template
for research talks with animated builds, a speaker script, and coauthor comments that a coding agent can act on. PairTalk's
slide engine, its comment panel and marked boxes, its presenter controls, its screenshot, script and bundle tools, and its
shared review site on Cloudflare started from that template; the idea of a comment loop that hands precise, slide-level
feedback to an agent is his too. The files derived from it say so in their first lines:

- `template/index.html`, `template/css/*.css`, `template/js/*.js`
- `tools/bundle.mjs`, `tools/script.mjs`, `tools/slide_shots.mjs`
- `cloudflare/functions/_middleware.js`, `cloudflare/schema.sql`, `cloudflare/wrangler.toml`, `cloudflare/tests/smoke.mjs`

PairTalk's own additions (the `pairtalk` command, the style vault and seeding, the skill, the example talk)
are under the repository's MIT license. The code derived from html-slide is shared under html-slide's own notice, which is
kept here as it asks:

> **Original template code**
>
> Permission is granted, free of charge, to use, copy, modify, and share the original software code in this repository, with
> or without modification. Keep this notice with copies of that code. The code is provided as is, without warranty of any
> kind.

None of html-slide's example slide content (its research content, photos, logos or screenshots) is included in PairTalk. The
bundled maths renderer, MathJax, keeps its own license (`template/vendor/mathjax/LICENSE`), and its fonts theirs.
