// A link is a vote; votes from important pages count more.
Deck.slide({
  id: 'VOTES', title: 'A link is a vote, and some voters count more', steps: 3,
  notes: [
    "Here is a tiny web: five pages, A to E.",
    "And here are their links. The idea behind PageRank is that <b>a link is a vote</b>. When page D links to page A, D's author is telling us A is worth reading.",
    "So the simplest score counts votes: links in. A and C get three each, B and D one, E none. By this count, C ties for first and B is far behind.",
    "But look at where B's one vote comes from: from A, the page everybody points to, and it is A's <b>only</b> link. A vote from an important page should count more. That makes the score recursive: a page is important if important pages link to it. Next, a way to make that precise."
  ],
  init(el, L) {
    const W = window.WEB;
    const parts = W.draw(L, el, {
      nodeFlags: () => ({ in: 0 }),
      linkFlags: (j, i) => (j + i === 'AB' ? { in: 1 } : { in: 1, dim: 3 }),
    });
    W.names.forEach(i => {
      const [x, y] = W.pos[i];
      L.circle(L.svg(el), x + 62, y - 58, 27, { fill: 'gold', in: 2, dim: i === 'A' || i === 'B' ? undefined : 3 });
      L.label(el, x + 62, y - 58, String(W.inlinks[i]), { anchor: 'c', size: 's', color: 'paper', in: 2, dim: i === 'A' || i === 'B' ? undefined : 3 });
    });
    ['C', 'D', 'E'].forEach(i => { L.flags(parts.nodes[i].c, { dim: 3 }); L.flags(parts.nodes[i].lab, { dim: 3 }); });
    const ab = parts.links.AB;
    ab.stroke.classList.add('vt-ab'); ab.tip.classList.add('vt-ab');
    L.label(el, 1560, 560, 'links in', { anchor: 'l', color: 'gold', in: 2, dim: 3 });
  },
  html: `<style>
    .slide[data-id="VOTES"] .vt-ab { transition: stroke 300ms ease, fill 300ms ease, opacity var(--t-fast) ease, stroke-dashoffset var(--t-draw) cubic-bezier(.45,0,.2,1); }
  </style>`,
  state: k => ({ hot: k >= 3 ? 1 : 0 }),
  draw(el, s, L) {
    const c = s.hot > 0.5 ? L.C.blue : L.C.ink2;
    el.querySelectorAll('.vt-ab').forEach(n => { if (n.tagName === 'path' && n.getAttribute('fill') !== 'none') n.setAttribute('fill', c); else n.setAttribute('stroke', c); n.setAttribute('stroke-width', s.hot > 0.5 ? 7 : 4); });
  }
});
