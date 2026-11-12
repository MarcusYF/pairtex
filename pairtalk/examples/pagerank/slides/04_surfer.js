// The random surfer: follow a random link, forever; count where it is.
(function () {
  const PATH = ['E', 'C', 'A', 'B', 'C', 'A', 'B', 'A', 'B'];   // eight clicks, each along a real link
  let dot, counts;
  Deck.slide({
    id: 'SURFER', title: 'A random surfer follows links forever', steps: 2,
    dur: k => (k === 1 ? 5200 : 900),
    notes: [
      "Imagine a surfer who starts on some page, here E, and never stops. On every page, the surfer picks one of its links at random and follows it.",
      "Let us watch eight clicks. From E to C, from C to A, A to B, and so on. The counters keep track of how often the surfer has been on each page. It keeps coming back to A and to B.",
      "Now let the surfer run for a very long time. The share of time spent on each page settles down: about 37 percent on A, 35 on B, 21 on C, and only 4 and 3 percent on D and E. <b>That share of time is PageRank.</b>"
    ],
    init(el, L) {
      const W = window.WEB;
      W.draw(L, el, { nodeFlags: () => ({ in: 0 }), linkFlags: () => ({ in: 0 }) });
      counts = {};
      const OFF = { A: [0, -100], B: [118, 0], C: [-118, 0], D: [-112, 46], E: [112, 46] };   // outside each node, clear of its links
      W.names.forEach(i => {
        const [x, y] = W.pos[i], [dx, dy] = OFF[i];
        counts[i] = L.label(el, x + dx, y + dy, '0', { anchor: 'c', size: 'l', color: 'purple', in: 1, out: 2 });
        L.label(el, x + dx, y + dy, `${Math.round(W.rank[i] * 100)}%`, { anchor: 'c', size: 'l', color: 'blue', in: 2 });
      });
      dot = L.circle(L.svg(el), 0, 0, W.R + 14, { color: 'gold', w: 8, in: 0, out: 2 });
      L.label(el, 1560, 560, 'visits', { anchor: 'l', color: 'purple', in: 1, out: 2 });
      L.label(el, 1560, 620, 'share of time', { anchor: 'l', color: 'blue', in: 2 });
    },
    state: k => ({ t: k >= 1 ? 1 : 0 }),
    draw(el, s, L) {
      const W = window.WEB, hops = PATH.length - 1, x = s.t * hops, h = Math.min(hops - 1, Math.floor(x)), f = x - h;
      const p = s.t >= 1 ? W.pos[PATH[hops]] : W.at(W.curve(PATH[h], PATH[h + 1]), Math.min(1, f));
      L.attrs(dot, { cx: p[0].toFixed(1), cy: p[1].toFixed(1) });
      const reached = Math.min(PATH.length, Math.floor(x + 0.5) + 1), seen = {};
      PATH.slice(0, s.t >= 1 ? PATH.length : reached).forEach(i => { seen[i] = (seen[i] || 0) + 1; });
      W.names.forEach(i => { counts[i].textContent = String(seen[i] || 0); });
    }
  });
})();
