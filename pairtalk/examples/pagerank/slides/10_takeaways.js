// Takeaways: three lines, one per click.
Deck.slide({
  id: 'TAKEAWAYS', title: 'Takeaways', steps: 2,
  notes: [
    "To sum up. First: a link is a vote, and a vote is worth the rank of the page that casts it.",
    "Second: PageRank is the share of time a random surfer spends on each page, an eigenvector of the link matrix.",
    "Third: the random jump makes that ranking unique, and power iteration finds it in a few dozen passes over the links, on any web."
  ],
  html: `
    <style>
      .slide[data-id="TAKEAWAYS"] .title { font-size: 64px; }
      .slide[data-id="TAKEAWAYS"] .tk { position: absolute; left: 200px; top: 320px; width: 1600px; font-size: 54px; line-height: 1.3; white-space: nowrap; }
      .slide[data-id="TAKEAWAYS"] .tk > div { margin-bottom: 96px; }
      .slide[data-id="TAKEAWAYS"] .tk .num { color: var(--gold); width: 1.6em; }
      .slide[data-id="TAKEAWAYS"] .tk b { color: var(--blue); }
    </style>
    <div class="tk">
      <div data-in="0"><span class="num">1</span>A link is a <b>vote</b>, worth the rank of the voter</div>
      <div data-in="1"><span class="num">2</span>PageRank is the <b>random surfer's share of time</b></div>
      <div data-in="2"><span class="num">3</span><b>Jumping</b> makes it unique; <b>power iteration</b> finds it fast</div>
    </div>`
});
