// The result: the ranking of the five pages, against the count of links in.
(function () {
  const ORDER = ['A', 'B', 'C', 'D', 'E'], BX = 520, BW = 150, GAP = 70, BASE = 760, MAXH = 500, MAXV = 0.4;
  Deck.slide({
    id: 'RANKING', title: 'One link from A puts B above C', steps: 1,
    notes: [
      "So here is the ranking of our five pages. A first, with 0.37; then B, with 0.35; then C, with 0.21; D and E far behind.",
      "Now compare with the simple vote count. C has three links in, B only one. Yet B ranks above C, because B's one link comes from A, the most important page, and it is the only link A gives. This is the whole idea in one picture: <b>a vote is worth the rank of the voter</b>, divided among its links."
    ],
    init(el, L) {
      const W = window.WEB, svg = L.svg(el);
      L.line(svg, BX - 40, BASE, BX + ORDER.length * (BW + GAP) - GAP + 40, BASE, { color: 'ink2', w: 3 });
      ORDER.forEach((i, n) => {
        const x = BX + n * (BW + GAP), v = W.rank[i], h = v / MAXV * MAXH;
        const bar = L.rect(svg, x, BASE - h, BW, h, { fill: i === 'B' ? 'blue' : 'ink3', r: 4, in: 0 });
        if (i !== 'A' && i !== 'B') L.flags(bar, { dim: 1 });
        L.label(el, x + BW / 2, BASE - h - 16, v.toFixed(2), { anchor: 'cb', color: i === 'B' ? 'blue' : 'ink', in: 0 });
        L.label(el, x + BW / 2, BASE + 24, i, { anchor: 'ct', size: 'l', in: 0 });
        L.label(el, x + BW / 2, BASE + 110, String(W.inlinks[i]), { anchor: 'ct', color: i === 'B' || i === 'C' ? 'gold' : 'ink2', in: 1 });
      });
      L.label(el, BX - 60, BASE + 130, 'links in', { anchor: 'r', color: 'gold', in: 1 });
      L.label(el, BX - 60, BASE - MAXH / 2, 'PageRank', { anchor: 'r', color: 'ink2', in: 0 });
    }
  });
})();
