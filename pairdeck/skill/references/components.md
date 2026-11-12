# Engine components

The engine is in `assets/engine/`: `deck.css`, `deck.js`, `icons.svg` and `fonts/`. A deck links to it by a URL prefix, written `{ENGINE}` below: `_deck/` when the engine is copied next to the deck (the default), or a shared path such as `/decks/_deck/` on a site that hosts the engine once. `pairdeck new` writes the page skeleton for you.

## Contents
1. Page skeleton
2. Slides
3. Steps and dimming
4. Animations
5. Icons
6. Interactions and hooks
7. Phones and accessibility
8. Snippets

## 1. Page skeleton

```html
<link rel="stylesheet" href="{ENGINE}deck.css">
<script defer src="{ENGINE}deck.js"></script>
…
<body>
<header class="dk-bar">
  <a href="…">← Back</a>                 <!-- where the reader came from -->
  <span class="dk-paper">Short title</span>
  <a href="…" target="_blank" rel="noopener">Source ↗</a>
</header>
<main class="dk-deck" aria-label="Slides: use the arrow keys or the buttons below">
  <section class="dk-slide"> … </section> …
</main>
<nav class="dk-nav" aria-label="Slides">
  <button type="button" data-dk-prev aria-label="Previous">←</button>
  <span class="dk-dots" aria-hidden="true"></span>
  <span data-dk-count aria-live="polite"></span>
  <button type="button" data-dk-next aria-label="Next">→</button>
</nav>
<script> /* this deck's interactions */ </script>
</body>
```

The engine adds the slide number, the section label, the dots and the counter, and it keeps `#N` in the URL so `deck.html#4` opens slide 4.

## 2. Slides

```html
<section class="dk-slide" data-label="Result 1">
  <div class="dk-inner">
    <h2 class="dk-h">Headline that states the point</h2>
    <figure class="dk-fig" style="max-width:900px"><svg viewBox="0 0 900 360">…</svg></figure>
    <p class="dk-take" data-step="1">The one takeaway.</p>
    <p class="dk-note" data-step="1">Caveat, source, or “Schematic, not data.”</p>
  </div>
</section>
```

Layout helpers:
- `.dk-cols`: an auto-fit grid of equal columns. `.dk-cols--2-1` and `.dk-cols--1-2` give unequal columns; all of them stack on phones.
- `.dk-list`: numbered takeaways (`.n` number, `.t` title, `.d` description).
- `.dk-sub`, `.dk-meta`: title-slide text.
- `.dk-cap`: a caption.
- `.dk-chip`: a small pill.
- `.dk-quote`: italics.
- `.dk-hint`: a sans-serif hint.

Colour helpers:
- `c-*` sets the text colour.
- In SVG, `f-*` sets fill, `s-*` stroke and `t-*` text fill.
- Roles: `people`, `creator`, `platform`, `good`, `bad`, `gold`, `teal`, plus `ink`, `muted`, `faint` and `line`.
- Soft fills: `f-*-soft`, including `f-teal-soft`.
- Lines: `ln`, `ln-thin`, `ln-thick`, `dash`.
- `knock` adds a background halo behind a label.

## 3. Steps and dimming

- `data-step="n"` on any element, including an SVG `<g>`, keeps it hidden until build step `n` of its slide. Step numbers need not be consecutive; the engine sorts the distinct values. → and click advance one step, then move to the next slide.
- `data-dim="n"` fades an element once step `n` is shown. Use it so that earlier takeaways recede.
- `.dk-rise` adds a small upward entrance and `.dk-pop` a scale-in, both together with `data-step`.

## 4. Animations

Each animation runs when its slide is current and its nearest `[data-step]` ancestor (if any) is shown. It resets when you leave the slide.

- `.dk-draw` on a `<path>`: the stroke draws in. A dashed path (`.dash` or any `stroke-dasharray`) fades in instead, because drawing would make it solid.
- `.dk-grow` on a `<rect>`: the bar grows from the left. Add `.dk-up` to grow from the bottom. Stagger bars with `style="transition-delay:.08s"`, `.16s`, and so on.
- `[data-count-to="0.71"]` on a text element: the number counts up. It accepts `data-decimals`, `data-prefix` and `data-suffix`.
- `.dk-flow` (marching dashes) and `.dk-pulse`: continuous. Use them sparingly.

## 5. Icons

```html
<svg x="70" y="40" width="56" height="56" class="icon c-creator"><use href="{ENGINE}icons.svg#creator"/></svg>
```
Icons: `person`, `robot`, `creator`, `item`, `platform`, `doc`, `search`, `spark`, `coin`, `model`, `shield`, `thief`, `trophy`, `dice`, `loop`, `target`, `chat`, `poison`. Draw any extra icon inline in the same style (see `style.md` §3). An external sprite does not load from `file://`, so serve the deck over HTTP (`pairdeck review` and `pairdeck qa` do) or bundle it.

## 6. Interactions and hooks

Put controls inside an element with `data-interactive`, so that clicks and swipes there do not advance the slide. Buttons inside a `[role="group"]` in `.dk-ctl` are spaced and wrap automatically.

```html
<div class="dk-ctl" data-interactive>
  <span>creators’ exploration rate</span>
  <span role="group" aria-label="Exploration rate" id="eps"></span>   <!-- buttons: class dk-btn, aria-pressed -->
  <input type="range" min="0" max="2" step="0.1" value="1" aria-label="Elasticity">
</div>
```

`window.Deck` provides:
- `Deck.on("enter", (index, slide) => {})`, called when a slide becomes current;
- `Deck.on("step", (index, step, slide) => {})`, called after every render;
- `Deck.go(i)`, `Deck.next()`, `Deck.prev()` and `Deck.index`.

The engine script is deferred, so register hooks after `DOMContentLoaded`:

```js
document.addEventListener("DOMContentLoaded", function () {
  if (window.Deck) Deck.on("enter", function (i, s) { if (s.querySelector("#my-chart")) draw(current); });
});
```

Build chart elements with `document.createElementNS("http://www.w3.org/2000/svg", tag)`. Keep the data in a small object at the top of the script, with a comment that names its source ("paper, Table 5"). If the script creates icons, build their URL from a plain string literal that ends in `icons.svg#` (for example `"{ENGINE}icons.svg#" + id`): `pairdeck bundle` rewrites such literals for single files, but it cannot rewrite template strings.

## 7. Phones and accessibility

- **Phones.** Below a width of 640, a figure whose SVG viewBox is wider than 520 gets a minimum width (70% of the viewBox width), and its figure scrolls sideways with a "scroll →" hint. A one-time tip suggests turning the phone sideways. Keep key labels inside the left two-thirds of wide figures, so the first view already makes sense.
- **Accessibility.** Slides carry `aria-roledescription` and `aria-label`. Give controls `aria-label`s and use `aria-pressed` on toggle buttons.
- **Reduced motion.** Under `prefers-reduced-motion` the engine shows final states without transitions. Custom scripts should do the same.

## 8. Snippets

**Actors and flow** (left to right, built in steps):
```html
<svg viewBox="0 -20 960 400">
  <g data-step="1" class="dk-rise">
    <svg x="70" y="150" width="56" height="56" class="icon c-creator"><use href="{ENGINE}icons.svg#creator"/></svg>
    <text x="98" y="240" text-anchor="middle" class="t-creator" font-size="24">creators</text>
  </g>
  <g data-step="2" class="dk-rise">
    <path class="ln s-creator dk-draw" d="M140 178 H380"/>
    <svg x="392" y="100" width="150" height="150" class="icon c-platform"><use href="{ENGINE}icons.svg#platform"/></svg>
    <text x="467" y="290" text-anchor="middle" class="t-platform" font-size="24">platform</text>
  </g>
</svg>
```

**Growing result bars** (direct labels and a dashed reference line):
```html
<path class="ln-thin s-good dash" d="M790 44 V330"/>
<text x="176" y="74" text-anchor="end" class="t-ink" font-size="19">K = 1</text>
<rect class="f-good dk-grow" x="190" y="56" width="300" height="28" rx="3"/>
<text x="502" y="77" class="t-good" font-size="19">≥ 50%</text>
```

**Number badge** (a gold circle with a number; the lint accepts small text inside `.dk-badge`):
```html
<g class="dk-badge"><circle cx="40" cy="40" r="14" class="f-gold"/><text x="40" y="45" text-anchor="middle" class="f-bg" font-size="14" font-weight="700">1</text></g>
```

**Takeaways:**
```html
<ol class="dk-list">
  <li data-step="1" data-dim="2" class="dk-rise"><span class="n">1</span><span class="t">Short title</span><span class="d">One sentence.</span></li>
  …
</ol>
<p class="dk-note" data-step="3"><a href="…">Paper page</a> · <a href="…" target="_blank" rel="noopener">arXiv</a></p>
```

For a complete, working deck with these patterns (actors, growing bars, a contrast, and a slider that redraws a chart), read `examples/simpsons-paradox/index.html` in the PairDeck repository (`pairdeck paths` names the code folder).
