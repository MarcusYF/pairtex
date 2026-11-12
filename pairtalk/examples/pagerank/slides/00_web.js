// Shared by the slides (no slide of its own): the five-page web, its links, and its PageRank, computed here so that every
// number on the slides is the real one.
(function () {
  const W = window.WEB = {};
  W.names = ['A', 'B', 'C', 'D', 'E'];
  W.links = { A: ['B'], B: ['A', 'C'], C: ['A'], D: ['C', 'A'], E: ['C', 'D'] };
  W.pos = { A: [960, 300], B: [1290, 500], C: [630, 500], D: [770, 830], E: [1150, 830] };
  W.R = 58;            // node radius
  W.alpha = 0.85;

  const n = W.names.length;
  W.step = r => {
    const out = {};
    W.names.forEach(i => { out[i] = (1 - W.alpha) / n; });
    W.names.forEach(j => W.links[j].forEach(i => { out[i] += W.alpha * r[j] / W.links[j].length; }));
    return out;
  };
  const uniform = () => Object.fromEntries(W.names.map(i => [i, 1 / n]));
  let r = uniform();
  for (let t = 0; t < 400; t++) r = W.step(r);
  W.rank = r;                                                    // A .37, B .35, C .21, D .04, E .03
  W.errors = (T) => {                                           // ||r(t) - r||_1 from the uniform start, t = 0..T
    const out = []; let x = uniform();
    for (let t = 0; t <= T; t++) { out.push(W.names.reduce((s, i) => s + Math.abs(x[i] - r[i]), 0)); x = W.step(x); }
    return out;
  };
  W.inlinks = Object.fromEntries(W.names.map(i => [i, W.names.filter(j => W.links[j].includes(i)).length]));

  // the curve of the link j -> i, centre to centre; a link that has a partner in the other direction bends to its own side
  W.curve = (j, i, pos = W.pos) => {
    const [x0, y0] = pos[j], [x1, y1] = pos[i], dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy);
    const both = (W.links[i] || []).includes(j), bend = both ? 46 : 0;
    const c = [(x0 + x1) / 2 - dy / len * bend, (y0 + y1) / 2 + dx / len * bend];
    return { p0: [x0, y0], c, p1: [x1, y1] };
  };
  W.at = (q, s) => {                                            // a point on a quadratic curve
    const u = 1 - s;
    return [u * u * q.p0[0] + 2 * u * s * q.c[0] + s * s * q.p1[0], u * u * q.p0[1] + 2 * u * s * q.c[1] + s * s * q.p1[1]];
  };
  // an arrow along the curve, trimmed to the node circles: a stroke (it draws in) and a head (it fades in)
  W.arrow = (L, svg, q, o = {}) => {
    const R = o.r || W.R, gap = 8, len = Math.hypot(q.p1[0] - q.p0[0], q.p1[1] - q.p0[1]);
    const s0 = (R + gap) / len, s1 = 1 - (R + gap) / len;
    const a = W.at(q, s0), b = W.at(q, s1), mid = W.at(q, 0.5);
    // the control point of the trimmed piece, so that it passes through the same middle point
    const c = [2 * mid[0] - (a[0] + b[0]) / 2, 2 * mid[1] - (a[1] + b[1]) / 2];
    const color = o.color || 'ink2', w = o.w || 4, head = o.head || 22;
    const ang = Math.atan2(b[1] - c[1], b[0] - c[0]);
    const tip = b, base = [b[0] - head * Math.cos(ang), b[1] - head * Math.sin(ang)];
    const px = -Math.sin(ang) * head * 0.48, py = Math.cos(ang) * head * 0.48;
    const g = L.g(svg, {});
    const flags = Object.assign({}, o.flags || {});
    const stroke = L.path(g, `M${a[0].toFixed(1)},${a[1].toFixed(1)} Q${c[0].toFixed(1)},${c[1].toFixed(1)} ${(base[0] + 0.3 * head * Math.cos(ang)).toFixed(1)},${(base[1] + 0.3 * head * Math.sin(ang)).toFixed(1)}`,
      Object.assign({ color, w, dash: o.dash }, flags, o.dash ? {} : { draw: flags.in !== undefined }));
    const tipPath = L.el(g, 'path', { d: `M${tip[0].toFixed(1)},${tip[1].toFixed(1)}L${(base[0] + px).toFixed(1)},${(base[1] + py).toFixed(1)}L${(base[0] - px).toFixed(1)},${(base[1] - py).toFixed(1)}Z`, fill: L.col(color) });
    L.flags(tipPath, flags);
    return { g, stroke, tip: tipPath };
  };
  // the web: nodes and links, each with its own build flags; returns the parts so a slide can recolour them
  W.draw = (L, el, o = {}) => {
    const svg = L.svg(el), parts = { nodes: {}, links: {} };
    const pos = o.pos || W.pos;
    W.names.forEach(j => W.links[j].forEach(i => {
      parts.links[j + i] = W.arrow(L, svg, W.curve(j, i, pos), { flags: (o.linkFlags || (() => ({})))(j, i), color: 'ink2' });
    }));
    W.names.forEach(i => {
      const [x, y] = pos[i], f = (o.nodeFlags || (() => ({})))(i);
      const c = L.circle(svg, x, y, W.R, Object.assign({ fill: 'paper', color: 'ink', w: 4 }, f));
      const lab = L.label(el, x, y, i, Object.assign({ anchor: 'c', size: 'l' }, f));
      parts.nodes[i] = { c, lab };
    });
    return parts;
  };
})();
