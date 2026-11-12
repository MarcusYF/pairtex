// Dead ends and traps; teleporting frees the surfer, and gives the formula with alpha.
(function () {
  const POS = { X: [330, 420], Y: [700, 420], R: [1160, 600], P: [1300, 360], Q: [1600, 420] };
  const LINKS = { X: ['Y'], Y: [], R: ['P'], P: ['Q'], Q: ['P'] };
  Deck.slide({
    id: 'STUCK', title: 'Teleporting frees a stuck surfer', steps: 3,
    notes: [
      "The first problem is a <b>dead end</b>: a page with no links out, like Y here. The surfer arrives and has nowhere to go.",
      "The second is a <b>trap</b>: P and Q link only to each other. Once the surfer is in, it circles there forever, and every page outside gets a share of zero.",
      "The fix is simple. At every step, with a small chance, the surfer ignores the links and <b>jumps to a page chosen at random</b>. Dead ends and traps can no longer hold it.",
      "In the formula, that is one extra term. With chance alpha the surfer follows a link, as before; with chance one minus alpha it jumps, and each of the n pages gets an equal share of that jump. The usual choice is alpha equal to 0.85: about six clicks, on average, before a jump."
    ],
    html: `
      <style>
        .slide[data-id="STUCK"] .st-eq { position: absolute; left: 0; right: 0; top: 720px; text-align: center; font-size: 60px; }
        .slide[data-id="STUCK"] .st-caps { position: absolute; left: 0; right: 0; top: 880px; display: flex; justify-content: center;
          align-items: baseline; gap: 60px; font-size: 36px; white-space: nowrap; }
      </style>
      <div class="st-eq" data-in="3">\\( r_i = \\class{c-blue}{\\alpha \\sum_{j \\to i} \\frac{r_j}{d_j}} + \\class{c-gold}{\\frac{1-\\alpha}{n}} \\)</div>
      <div class="st-caps" data-in="3"><span class="c-blue">follow a link · \\( \\alpha = 0.85 \\)</span><span class="c-gold">jump to any of \\( n \\) pages</span></div>`,
    init(el, L) {
      const W = window.WEB, svg = L.svg(el);
      const side = { X: 0, Y: 0, R: 1, P: 1, Q: 1 };
      const both = (a, b) => LINKS[b].includes(a);
      Object.keys(LINKS).forEach(j => LINKS[j].forEach(i => {
        const [x0, y0] = POS[j], [x1, y1] = POS[i], len = Math.hypot(x1 - x0, y1 - y0), bend = both(j, i) ? 46 : 0;
        const q = { p0: POS[j], c: [(x0 + x1) / 2 - (y1 - y0) / len * bend, (y0 + y1) / 2 + (x1 - x0) / len * bend], p1: POS[i] };
        W.arrow(L, svg, q, { flags: { in: side[j] }, color: 'ink2', r: 52 });
      }));
      Object.keys(POS).forEach(i => {
        const [x, y] = POS[i];
        L.circle(svg, x, y, 52, { fill: 'paper', color: 'ink', w: 4, in: side[i] });
        L.label(el, x, y, i, { anchor: 'c', size: 'l', in: side[i] });
      });
      L.label(el, 515, 520, 'dead end', { anchor: 'c', color: 'red', in: 0 });
      L.label(el, 1450, 250, 'trap', { anchor: 'c', color: 'red', in: 1 });
      L.circle(svg, POS.Y[0] + 50, POS.Y[1] - 50, 18, { fill: 'gold', in: 0 });
      L.circle(svg, POS.Q[0] + 50, POS.Q[1] - 50, 18, { fill: 'gold', in: 1 });
      // the jumps: dashed gold arcs from the stuck pages to the others
      const jump = (a, b, bend) => {
        const [x0, y0] = POS[a], [x1, y1] = POS[b], len = Math.hypot(x1 - x0, y1 - y0);
        const q = { p0: POS[a], c: [(x0 + x1) / 2 - (y1 - y0) / len * bend, (y0 + y1) / 2 + (x1 - x0) / len * bend], p1: POS[b] };
        W.arrow(L, svg, q, { flags: { in: 2 }, color: 'gold', r: 52, dash: '12 10', w: 4 });
      };
      jump('Y', 'X', 120); jump('Q', 'R', -120);
      L.label(el, 515, 312, 'jump', { anchor: 'c', color: 'gold', in: 2 });
      L.label(el, 1470, 650, 'jump', { anchor: 'c', color: 'gold', in: 2 });
    }
  });
})();
