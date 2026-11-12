// The chart: power iteration on the five-page web, measured error against the theorem's bound (log scale).
(function () {
  const T = 30, X0 = 380, Y0 = 880, PW = 1200, PH = 600, LO = -8;     // y axis: log10 of the error, from 10^-8 to 10^0
  const X = t => X0 + t / T * PW, Y = v => Y0 - (Math.log10(v) - LO) / -LO * PH;
  Deck.slide({
    id: 'CONVERGE', title: 'The error shrinks geometrically', steps: 2,
    notes: [
      "Here is power iteration on our five-page web. The horizontal axis counts the steps; the vertical axis is the error, the distance to the true ranking, on a log scale, so a straight line means a constant factor per step.",
      "Starting from the uniform guess, these are the measured errors. After ten steps the error is about one in a thousand; after twenty, about one in a hundred thousand.",
      "The dashed line is what the theorem guarantees: a factor 0.85 per step. The real error falls much faster here, because this web is small and well connected. On the whole web, the guarantee is what you plan for: about 57 steps cut the error ten thousand times, whatever the size of the web. That is why PageRank was practical: one pass over the links per step, a few dozen steps."
    ],
    init(el, L) {
      const W = window.WEB, svg = L.svg(el), err = W.errors(T);
      const P = { x0: X0, y0: Y0, w: PW, h: PH };
      L.arrow(svg, X0, Y0, X0 + PW + 40, Y0, { color: 'ink2', w: 3, head: 20 });
      L.arrow(svg, X0, Y0, X0, Y0 - PH - 40, { color: 'ink2', w: 3, head: 20 });
      [0, 10, 20, 30].forEach(t => { L.line(svg, X(t), Y0 - 8, X(t), Y0 + 8, { color: 'ink2', w: 3 }); L.label(el, X(t), Y0 + 22, String(t), { anchor: 'ct', size: 's', color: 'ink2' }); });
      [0, -2, -4, -6, -8].forEach(e => {
        const y = Y(Math.pow(10, e));
        L.line(svg, X0 - 8, y, X0 + 8, y, { color: 'ink2', w: 3 });
        if (e < 0) L.line(svg, X0 + 10, y, X0 + PW, y, { color: 'rule', w: 2 });
        L.label(el, X0 - 22, y, e === 0 ? '1' : `\\( 10^{${e}} \\)`, { anchor: 'r', size: 's', color: 'ink2' });
      });
      L.label(el, X0 + PW / 2, Y0 + 74, 'iteration \\( t \\)', { anchor: 'ct', color: 'ink2' });
      L.label(el, X0 + 24, Y0 - PH - 40, 'error \\( \\lVert r^{(t)} - r \\rVert_1 \\)', { anchor: 'lb', color: 'ink' });
      const pts = err.map((e, t) => [X(t), Y(e)]);
      L.poly(svg, pts, { color: 'blue', w: 4, in: 1, draw: true });
      pts.forEach(p => L.dot(svg, p[0], p[1], { r: 9, fill: 'blue', in: 1 }));
      L.label(el, X(30) + 26, Y(err[30]), 'measured', { anchor: 'l', color: 'blue', in: 1 });
      const bound = [0, T].map(t => [X(t), Y(err[0] * Math.pow(W.alpha, t))]);
      L.poly(svg, bound, { color: 'gold', w: 5, dash: '16 12', in: 2 });
      L.label(el, X(30) + 26, Y(err[0] * Math.pow(W.alpha, T)), 'guarantee \\( 0.85^t \\)', { anchor: 'l', color: 'gold', in: 2 });
    }
  });
})();
