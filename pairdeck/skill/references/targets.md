# Where a deck can live

Decide the target early: it sets the engine URL, the links, and what to deliver. Publishing anywhere needs the author's
explicit go-ahead.

## 1. A standalone folder (the default)

`pairdeck new <slug> --dir <folder>` copies the engine to `<folder>/_deck/`. The folder can be zipped, synced, or uploaded to any
static host as is. Open it through a local server (`pairdeck review <slug>`, or `python3 -m http.server`), not `file://`,
because the external icon sprite does not load from `file://`. Or make a single file.

## 2. One self-contained file

```bash
pairdeck bundle <slug>                      # writes dist/<slug>.html in the deck's folder
pairdeck bundle <slug> -o ~/Desktop/deck.html --no-fonts
```

The CSS, the JS, the icons the deck uses, local images and the fonts are inlined, so the file opens from `file://`, from
e-mail, in a learning-management system, or as a single published page. With the fonts it is about 0.6 MB; `--no-fonts` falls
back to Latin Modern or Georgia and saves about 0.5 MB, for a viewer with a size limit. Root-relative links (`/papers/…`) stop
working outside the original site, and `bundle` lists them: make them absolute. Run `pairdeck qa` on the bundled file before
sending it anywhere.

For readers on a phone who cannot open HTML, the light-mode screenshots from `pairdeck qa` (one per slide, plus one per
interaction state with `--after`/`--tag`) make a fine PDF; combine them with the platform's own tools.

## 3. A website that hosts the engine once

Copy `assets/engine/` once to a shared path on the site (for example `/decks/_deck/`), then scaffold every deck there with
`pairdeck new <slug> --dir <site>/static/decks/<slug> --engine-url /decks/_deck/`. `pairdeck qa` finds a root-relative engine by
searching upwards from the deck. When PairDeck's engine improves later, update that one copy, with the author's approval: the
change reaches every deck that uses it.

- Use lowercase slugs: some hosts redirect mixed-case URLs.
- For a public page, add `og:url` and `og:image` with absolute URLs; `pairdeck card <slug> --site example.org` renders the
  1200×630 image from the title slide.
- Follow the site's own checks and review before publishing, and stage only the deck's files when committing to a shared
  repository.

## 4. A course page or another site

Ask where the deck should go and follow that repository's docs. Set the back link to the page the reader comes from, and on the
last slide link the related pages. Until the placement is known, deliver a standalone folder and leave the back link out.

## Engine copies and updates

Every copy of the engine (a deck's `_deck/`, a site's shared copy) is a snapshot. A deck keeps working with the copy it was
built with; updating a published copy is the author's decision.
