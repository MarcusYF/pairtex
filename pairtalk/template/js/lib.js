// Derived from html-slide by Yanwei Sun (https://github.com/Yanwei-Sun/html-slide); see NOTICE.md.
// Figure helpers: SVG geometry and HTML labels in 1920 × 1080 stage coordinates.
(function () {
  const L = Deck.lib, NS = 'http://www.w3.org/2000/svg';
  const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  L.C = {};
  ['paper', 'ink', 'ink2', 'ink3', 'rule', 'wash', 'blue', 'gold', 'teal', 'orange', 'green', 'red', 'purple']
    .forEach(k => { L.C[k] = cssv('--' + k); });
  const col = c => (c && L.C[c]) || c || L.C.ink;
  L.col = col;

  L.attrs = function (n, a) { for (const k in a) if (a[k] !== undefined && a[k] !== null) n.setAttribute(k, a[k]); return n; };
  L.el = function (parent, tag, a) { const n = document.createElementNS(NS, tag); L.attrs(n, a || {}); if (parent) parent.appendChild(n); return n; };
  L.svg = function (el) {
    let s = el.querySelector(':scope > svg.fig');
    if (!s) { s = L.el(null, 'svg', { class: 'fig', viewBox: '0 0 1920 1080' }); el.insertBefore(s, el.firstChild); }
    return s;
  };
  L.g = (p, a) => L.el(p, 'g', a);
  // build flags on SVG nodes and labels: o.in / o.out / o.dim / o.undim -> data-* attributes
  function flags(n, o) {
    if (!o) return n;
    ['in', 'out', 'dim', 'undim'].forEach(k => { if (o[k] !== undefined) n.setAttribute('data-' + k, o[k]); });
    if (o.draw) n.classList.add('draw');
    if (o.cls) o.cls.split(' ').forEach(c => n.classList.add(c));
    if (o.id) n.id = o.id;
    return n;
  }
  L.flags = flags;

  // ---------- shapes ----------
  L.line = function (p, x1, y1, x2, y2, o = {}) {
    return flags(L.el(p, 'line', { x1, y1, x2, y2, stroke: col(o.color || 'ink'), 'stroke-width': o.w || 4,
      'stroke-linecap': o.cap || 'round', 'stroke-dasharray': o.dash, opacity: o.op }), o);
  };
  L.path = function (p, d, o = {}) {
    return flags(L.el(p, 'path', { d, fill: o.fill ? col(o.fill) : 'none', 'fill-opacity': o.fop, stroke: o.color === 'none' ? 'none' : col(o.color || 'ink'),
      'stroke-width': o.w === undefined ? 4 : o.w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': o.dash, opacity: o.op }), o);
  };
  L.poly = function (p, pts, o = {}) { return L.path(p, 'M' + pts.map(q => q[0].toFixed(1) + ',' + q[1].toFixed(1)).join('L') + (o.close ? 'Z' : ''), o); };
  L.circle = function (p, cx, cy, r, o = {}) {
    return flags(L.el(p, 'circle', { cx, cy, r, fill: o.fill ? col(o.fill) : 'none', stroke: o.color ? col(o.color) : 'none',
      'stroke-width': o.w || 3.5, opacity: o.op }), o);
  };
  L.dot = (p, x, y, o = {}) => L.circle(p, x, y, o.r || 11, Object.assign({ fill: o.fill || 'ink' }, o));
  L.ring = (p, x, y, o = {}) => L.circle(p, x, y, o.r || 22, Object.assign({ color: o.color || 'ink', w: o.w || 3.5 }, o));
  L.at = function (n, x, y) { if (n.tagName === 'circle') L.attrs(n, { cx: x, cy: y }); else n.setAttribute('transform', `translate(${x},${y})`); return n; };
  L.seg = (n, x1, y1, x2, y2) => L.attrs(n, { x1, y1, x2, y2 });
  L.rect = function (p, x, y, w, h, o = {}) {
    return flags(L.el(p, 'rect', { x, y, width: w, height: h, rx: o.r === undefined ? 8 : o.r, fill: o.fill ? col(o.fill) : 'none', 'fill-opacity': o.fop,
      stroke: o.color ? col(o.color) : 'none', 'stroke-width': o.w || 3, opacity: o.op }), o);
  };

  // arrow from (x1,y1) to (x2,y2); returns a group whose geometry L.setArrow can update
  L.arrow = function (p, x1, y1, x2, y2, o = {}) {
    const g = flags(L.g(p, { opacity: o.op }), o);
    g._line = L.line(g, x1, y1, x2, y2, { color: o.color || 'ink', w: o.w || 4, dash: o.dash });
    g._head = L.el(g, 'path', { fill: col(o.color || 'ink') });
    g._size = o.head || 18;
    L.setArrow(g, x1, y1, x2, y2);
    return g;
  };
  L.setArrow = function (g, x1, y1, x2, y2) {
    const len = Math.hypot(x2 - x1, y2 - y1);
    if (len < 0.5) { L.seg(g._line, x1, y1, x1, y1); g._head.setAttribute('d', ''); return g; }   // nothing to draw yet
    // the head never outgrows the arrow, so an arrow growing from zero length has no backward stub
    const a = Math.atan2(y2 - y1, x2 - x1), s = Math.min(g._size, len), bx = x2 - s * Math.cos(a), by = y2 - s * Math.sin(a);
    L.seg(g._line, x1, y1, bx + 0.4 * s * Math.cos(a), by + 0.4 * s * Math.sin(a));
    const px = -Math.sin(a) * s * 0.5, py = Math.cos(a) * s * 0.5;
    g._head.setAttribute('d', `M${x2},${y2}L${bx + px},${by + py}L${bx - px},${by - py}Z`);
    return g;
  };

  // ---------- plots ----------
  L.plot = function (o) {
    const P = Object.assign({ xmax: 1, ymax: 1 }, o);
    P.X = v => P.x0 + (v / P.xmax) * P.w;
    P.Y = v => P.y0 - (v / P.ymax) * P.h;
    P.pt = (x, y) => [P.X(x), P.Y(y)];
    return P;
  };
  // axes with arrowheads; labels: o.x / o.y (math, colored via o.xColor / o.yColor), o.xNote / o.yNote (grey words)
  L.axes = function (el, P, o = {}) {
    const svg = L.svg(el), g = flags(L.g(svg), o.flags);
    const ext = o.ext === undefined ? 40 : o.ext;
    L.arrow(g, P.x0, P.y0, P.x0 + P.w + ext, P.y0, { color: 'ink2', w: 3, head: 20 });
    L.arrow(g, P.x0, P.y0, P.x0, P.y0 - P.h - ext, { color: 'ink2', w: 3, head: 20 });
    const lab = [];
    if (o.origin !== false) lab.push(L.label(el, P.x0 - 14, P.y0 + 12, '0', { anchor: 'rt', size: 's', color: 'ink2' }));
    if (o.x) lab.push(L.label(el, P.x0 + P.w + ext + 18, P.y0, o.x, { anchor: 'l', color: o.xColor || 'ink' }));
    if (o.xNote) lab.push(L.label(el, P.x0 + P.w / 2, P.y0 + 30, o.xNote, { anchor: 'ct', size: 's', color: 'ink2' }));
    if (o.y) lab.push(L.label(el, P.x0 + 20, P.y0 - P.h - ext - 6, o.y, { anchor: 'lb', color: o.yColor || 'ink' }));
    if (o.yNote) lab.push(L.label(el, P.x0 + 20 + (o.yNoteDx || 110), P.y0 - P.h - ext - 10, o.yNote, { anchor: 'lb', size: 's', color: 'ink2' }));
    (o.xticks || []).forEach(t => { L.line(g, P.X(t[0]), P.y0 - 8, P.X(t[0]), P.y0 + 8, { color: 'ink2', w: 3 });
      lab.push(L.label(el, P.X(t[0]), P.y0 + 24, t[1], { anchor: 'ct', size: 's', color: 'ink2' })); });   // clear of the tick mark
    if (o.flags) lab.forEach(n => flags(n, o.flags));
    return { g, labels: lab };
  };
  L.curve = function (p, P, f, a, b, o = {}) {
    const n = o.n || 80, pts = [];
    for (let i = 0; i <= n; i++) { const x = a + (b - a) * i / n; pts.push(P.pt(x, f(x))); }
    return L.poly(p, pts, o);
  };

  // ---------- HTML labels ----------
  const ANCH = { l: [0, -50], r: [-100, -50], c: [-50, -50], t: [-50, 0], b: [-50, -100], lt: [0, 0], lb: [0, -100], rt: [-100, 0], rb: [-100, -100], ct: [-50, 0], cb: [-50, -100] };
  L.label = function (el, x, y, html, o = {}) {
    const d = document.createElement('div');
    d.className = 'lab' + (o.size ? ' ' + o.size : '');
    d.innerHTML = html;
    if (o.color) d.style.color = col(o.color);
    if (o.width) { d.style.whiteSpace = 'normal'; d.style.width = o.width + 'px'; }
    if (o.align) d.style.textAlign = o.align;
    if (o.style) d.setAttribute('style', d.getAttribute('style') + ';' + o.style);
    d._anchor = ANCH[o.anchor || 'lb'];
    L.place(d, x, y);
    flags(d, o);
    el.appendChild(d);
    return d;
  };
  L.place = function (d, x, y) { const a = d._anchor || ANCH.lb; d.style.left = x + 'px'; d.style.top = y + 'px'; d.style.transform = `translate(${a[0]}%,${a[1]}%)`; return d; };

  // ---------- icons (drawn in a 100x100 box centred on (x, y)) ----------
  L.icon = function (p, name, x, y, size = 90, o = {}) {
    const c = col(o.color || 'ink'), w = o.w || 5;
    const g = flags(L.g(p, { transform: `translate(${x - size / 2},${y - size / 2}) scale(${size / 100})` }), o);
    const S = { fill: 'none', stroke: c, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    const E = (tag, a) => L.el(g, tag, Object.assign({}, S, a));
    const F = (tag, a) => L.el(g, tag, Object.assign({ fill: c, stroke: 'none' }, a));
    switch (name) {
      case 'robot': E('rect', { x: 16, y: 30, width: 68, height: 54, rx: 14 }); F('circle', { cx: 38, cy: 54, r: 6 }); F('circle', { cx: 62, cy: 54, r: 6 });
        E('line', { x1: 40, y1: 71, x2: 60, y2: 71 }); E('line', { x1: 50, y1: 30, x2: 50, y2: 16 }); F('circle', { cx: 50, cy: 12, r: 5 }); break;
      case 'person': F('circle', { cx: 50, cy: 30, r: 17 }); F('path', { d: 'M18,92 C18,62 32,54 50,54 C68,54 82,62 82,92 Z' }); break;
      case 'person-o': E('circle', { cx: 50, cy: 30, r: 16 }); E('path', { d: 'M20,90 C20,63 33,55 50,55 C67,55 80,63 80,90' }); break;
      case 'firm': E('rect', { x: 18, y: 34, width: 64, height: 54, rx: 4 }); E('path', { d: 'M18,34 L50,14 L82,34' });
        [30, 46, 62].forEach(xx => E('line', { x1: xx + 4, y1: 50, x2: xx + 4, y2: 72 })); break;
      case 'server': [13, 40, 67].forEach(yy => { E('rect', { x: 19, y: yy, width: 62, height: 21, rx: 5 });   // a server rack
        E('line', { x1: 30, y1: yy + 10.5, x2: 50, y2: yy + 10.5 }); F('circle', { cx: 69, cy: yy + 10.5, r: 3.8 }); }); break;
      case 'doc': E('path', { d: 'M24,10 H62 L78,26 V90 H24 Z' }); E('path', { d: 'M62,10 V26 H78' });
        [42, 56, 70].forEach(yy => E('line', { x1: 36, y1: yy, x2: 66, y2: yy })); break;
      case 'chat': E('path', { d: 'M14,20 H86 V66 H44 L26,84 V66 H14 Z' }); break;
      case 'check': E('path', { d: 'M18,54 L40,76 L84,26', 'stroke-width': w * 1.6 }); break;
      case 'cross': E('path', { d: 'M24,24 L76,76 M76,24 L24,76', 'stroke-width': w * 1.5 }); break;
      case 'coin': E('circle', { cx: 50, cy: 50, r: 34 }); L.el(g, 'text', { x: 50, y: 64, 'text-anchor': 'middle', 'font-size': 42, fill: c, 'font-family': 'CM, serif' }).textContent = '$'; break;
      case 'clock': E('circle', { cx: 50, cy: 50, r: 36 }); E('path', { d: 'M50,28 V50 L64,60' }); break;
      case 'tokens': [0, 1, 2].forEach(i => E('rect', { x: 12 + i * 27, y: 36, width: 22, height: 28, rx: 5 })); break;
      case 'queue': [0, 1, 2, 3].forEach(i => E('rect', { x: 6 + i * 23, y: 34, width: 19, height: 32, rx: 4 })); break;
      case 'search': E('circle', { cx: 42, cy: 42, r: 25 }); E('line', { x1: 61, y1: 61, x2: 84, y2: 84, 'stroke-width': w * 1.6 }); break;
      case 'globe': E('circle', { cx: 50, cy: 50, r: 36 }); E('ellipse', { cx: 50, cy: 50, rx: 16, ry: 36 });
        E('line', { x1: 14, y1: 50, x2: 86, y2: 50 }); E('path', { d: 'M20,31 H80 M20,69 H80' }); break;
      case 'link': E('rect', { x: 10, y: 38, width: 46, height: 24, rx: 12 }); E('rect', { x: 44, y: 38, width: 46, height: 24, rx: 12 }); break;
      default: E('rect', { x: 10, y: 10, width: 80, height: 80, rx: 10 });
    }
    return g;
  };

  // ---------- animation helpers ----------
  L.tween = (ms, fn, tok) => Deck.tween(ms, fn, tok);
  L.wait = (ms, tok) => Deck.wait(ms, tok);
  L.mix = (a, b, t) => a + (b - a) * t;
  L.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  // piecewise progress: sub(t, a, b) maps t in [a,b] to [0,1] (for staging inside one tween)
  L.sub = (t, a, b) => L.clamp((t - a) / (b - a));
  L.op = (n, v) => { n.style.opacity = v; return n; };
})();

/* Section cards: Deck.sectionCard({ id, index, title, sub }). Set Deck.lib.SECTIONS (the talk's parts, in order) in
   slides/order.js or a slide file; `index` picks the part the card opens, and the outline along the bottom highlights it. */
(function () {
  const L = Deck.lib;
  L.SECTIONS = L.SECTIONS || [];
  Deck.sectionCard = function (o) {
    const out = L.SECTIONS.map((s, i) => `<span class="${i === o.index ? 'on' : ''}">${s}</span>`).join('');
    Deck.slide({ id: o.id, name: o.title, kind: 'section-card', steps: 0, backup: o.backup, title: null, section: L.SECTIONS[o.index], notes: o.notes,
      html: `<div class="sc-title" data-in="0">${o.title}</div><div class="sc-line" data-in="0"></div>` +
            (o.sub ? `<div class="sc-sub" data-in="0" style="top:540px">${o.sub}</div>` : '') +
            (o.outline === false || !L.SECTIONS.length ? '' : `<div class="outline">${out}</div>`) });
  };
})();
