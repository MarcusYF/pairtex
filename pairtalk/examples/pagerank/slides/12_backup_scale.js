// Backup: the same update on the whole web.
Deck.slide({
  id: 'SCALE', title: 'The same update on the whole web', steps: 0, backup: true,
  notes: [
    "This slide is for the question of scale. Each step is one pass over all links, so the cost per step grows with the number of links, not with the square of the number of pages. The guarantee from the theorem does not depend on the size of the web at all: 57 steps cut the error ten thousand times at alpha 0.85. Dead ends are handled by letting them link to every page."
  ],
  html: `
    <div class="rows big" style="left:240px;top:320px;width:1460px">
      <div><span class="num">1</span>One step = one pass over all links</div>
      <div><span class="num">2</span>Error cut \\( 10^{4} \\) times after \\( t \\ge \\log 10^{4} / \\log (1/0.85) \\approx 57 \\) steps</div>
      <div><span class="num">3</span>A dead end links to every page</div>
    </div>`
});
