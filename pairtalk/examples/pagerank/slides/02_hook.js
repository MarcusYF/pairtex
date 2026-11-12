// The hook: matching is easy, ordering is the problem.
(function () {
  const ROWS = ['pagerank-explained.example', 'linear-algebra-notes.example', 'search-engines-101.example', 'random-walks.example', 'web-graph-data.example'];
  Deck.slide({
    id: 'HOOK', title: 'Many pages match. Which should come first?', steps: 2,
    notes: [
      "Let me start with something you do every day. You type a query, say <b>pagerank</b>, into a search box.",
      "Thousands of pages contain that word. Finding them is the easy part: an index of words does it in milliseconds.",
      "The hard part is the <b>order</b>. You will read the first three results, maybe five. So the real question is: which page goes first? Word counts cannot answer it, because anyone can repeat a word. We need a signal the page cannot write about itself."
    ],
    html: `
      <style>
        .slide[data-id="HOOK"] .hk-box { position: absolute; left: 520px; top: 210px; width: 880px; height: 96px; border: 3px solid var(--ink2); border-radius: 48px; }
        .slide[data-id="HOOK"] .hk-q { position: absolute; left: 600px; top: 210px; height: 96px; line-height: 96px; font-size: 48px; }
        .slide[data-id="HOOK"] .hk-row { position: absolute; left: 520px; width: 880px; height: 92px; border-bottom: 2px solid var(--rule); font-size: 40px; line-height: 92px; }
        .slide[data-id="HOOK"] .hk-row .hk-n { display: inline-block; width: 92px; text-align: center; color: var(--gold); font-size: 44px; }
        .slide[data-id="HOOK"] .hk-row .hk-ok { position: absolute; right: 20px; top: 0; color: var(--green); font-size: 40px; }
      </style>
      <div class="hk-box" data-in="0"></div>
      <div class="hk-q" data-in="0">pagerank</div>
      ${ROWS.map((r, i) => `<div class="hk-row" data-in="1" style="top:${370 + i * 106}px;transition-delay:${i * 90}ms">`
        + `<span class="hk-n"><span data-in="2">?</span></span>${r}<span class="hk-ok">✓ match</span></div>`).join('')}`,
    init(el, L) { L.icon(L.svg(el), 'search', 1340, 258, 64, { color: 'ink2', in: 0 }); }
  });
})();
