// The theorem: with teleporting, exactly one ranking, and repeated multiplication finds it.
Deck.slide({
  id: 'THEOREM', title: 'With teleporting, there is exactly one ranking', steps: 1,
  notes: [
    "And with the jump, both questions have a clean answer. If every page has a link out, which we arrange by letting a dead end link to every page, and alpha is strictly between zero and one, then there is <b>exactly one</b> ranking: one vector r, nonnegative, summing to one, that solves the equation. This is the Perron–Frobenius theorem at work: thanks to the jump, every page can reach every other page.",
    "It also tells us how to compute it. Start from any guess, apply the update again and again, and the error shrinks by a factor of at least alpha at every step. With alpha 0.85, that is a guarantee of fifteen percent less error per step. Let us see how fast it really goes."
  ],
  html: `
    <style>
      .slide[data-id="THEOREM"] .th-box { left: 230px; top: 236px; width: 1460px; font-size: 40px; line-height: 1.45; padding: 36px 48px 30px; }
      .slide[data-id="THEOREM"] .th-d { text-align: center; font-size: 48px; margin: 18px 0 22px; }
      .slide[data-id="THEOREM"] .th-cite { position: absolute; left: 230px; top: 900px; font-size: 32px; color: var(--ink3); }
    </style>
    <div class="result th-box" data-in="0">
      <div><span class="kind">Theorem</span><span class="name">(informal)</span></div>
      <div class="row">If every page has a link out and \\( 0 < \\alpha < 1 \\), exactly one \\( r \\) with \\( r_i \\ge 0 \\) and \\( \\sum_i r_i = 1 \\) solves</div>
      <div class="th-d">\\( r_i = \\alpha \\sum_{j \\to i} \\frac{r_j}{d_j} + \\frac{1-\\alpha}{n} \\quad \\text{for every page } i. \\)</div>
      <div data-in="1">Repeating this update from any start converges to it:</div>
      <div class="th-d" data-in="1" style="margin-bottom:0">\\( \\lVert r^{(t)} - r \\rVert_1 \\le \\class{c-gold}{\\alpha^t} \\, \\lVert r^{(0)} - r \\rVert_1 \\)</div>
    </div>
    <div class="th-cite" data-in="0">Perron–Frobenius theorem · Banach fixed-point theorem</div>`
});
