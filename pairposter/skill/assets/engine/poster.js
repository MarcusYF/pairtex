/* PairPoster engine: sizes the page from <meta name="pairposter">, fits it to the window, zooms and pans, and prints it at
   its real size. URL options: ?export=1 fits the page exactly to the window with no controls (PNG export);
   ?view=x,y,w,h shows that part of the page (fractions) filling the window (QA close-ups).
   Keys: + and - zoom, 0 or f fits, 1 shows print size (1 CSS mm per mm), p plays the builds. Ctrl or pinch + scroll
   zooms at the pointer. */
(function () {
  "use strict";
  var root = document.documentElement;
  var meta = document.querySelector('meta[name="pairposter"]');
  var cfg = {};
  try { cfg = JSON.parse(meta ? meta.getAttribute("content") : "{}") || {}; } catch (e) { cfg = {}; }
  var W = +cfg.width_mm || 1189, H = +cfg.height_mm || 841;
  root.style.setProperty("--pp-w", W + "mm");
  root.style.setProperty("--pp-h", H + "mm");
  var page = document.createElement("style");
  page.textContent = "@page { size: " + W + "mm " + H + "mm; margin: 0; }";
  document.head.appendChild(page);

  var q = new URLSearchParams(location.search);
  var exportMode = q.has("export") || q.has("view");
  var region = (q.get("view") || "").split(",").map(Number);
  if (exportMode) root.classList.add("pp-export");

  var view, sizer, poster, ui, zoomLabel, scale = 1, fitting = true, M = 28;

  function px() { return { w: poster.offsetWidth, h: poster.offsetHeight }; }
  function apply(s) {
    scale = s;
    root.style.setProperty("--pp-scale", String(s));
    var d = px();
    sizer.style.width = d.w * s + "px";
    sizer.style.height = d.h * s + "px";
    if (exportMode) { sizer.style.margin = "0"; }
    else {
      var top = Math.max(M, (view.clientHeight - d.h * s) / 2), side = Math.max(M, (view.clientWidth - d.w * s) / 2);
      sizer.style.margin = top + "px " + side + "px";
    }
    if (zoomLabel) zoomLabel.textContent = Math.round(s * 100) + "%";
    window.dispatchEvent(new CustomEvent("poster:zoom", { detail: { scale: s } }));
  }
  function fit() {
    var d = px();
    fitting = true;
    if (exportMode) {
      // By width: the export window has the page's (or the region's) proportions, and headless Chrome can report a
      // slightly shorter innerHeight than the window it shoots.
      if (region.length === 4 && region.every(isFinite)) {
        var s = window.innerWidth / (region[2] * d.w);
        apply(s);
        view.scrollLeft = region[0] * d.w * s;
        view.scrollTop = region[1] * d.h * s;
      } else apply(window.innerWidth / d.w);
      return;
    }
    apply(Math.min((view.clientWidth - 2 * M) / d.w, (view.clientHeight - 2 * M) / d.h));
  }
  function zoomTo(s, cx, cy) {
    s = Math.max(0.05, Math.min(4, s));
    var r = view.getBoundingClientRect();
    cx = cx == null ? r.width / 2 : cx - r.left;
    cy = cy == null ? r.height / 2 : cy - r.top;
    var ox = (view.scrollLeft + cx - sizer.offsetLeft) / scale, oy = (view.scrollTop + cy - sizer.offsetTop) / scale;
    fitting = false;
    apply(s);
    view.scrollLeft = ox * s + sizer.offsetLeft - cx;
    view.scrollTop = oy * s + sizer.offsetTop - cy;
    window.dispatchEvent(new Event("resize"));
  }
  /* Builds: parts with data-build="N" appear in order of N, on screen only. */
  var playing = null;
  function play() {
    var els = Array.prototype.slice.call(document.querySelectorAll(".pp-poster [data-build]"));
    if (!els.length || exportMode || window.PP_NO_BUILD) return;
    var groups = {};
    els.forEach(function (e) { var k = +e.getAttribute("data-build") || 0; (groups[k] = groups[k] || []).push(e); e.classList.remove("pp-on"); });
    var keys = Object.keys(groups).map(Number).sort(function (a, b) { return a - b; });
    if (playing) playing.forEach(clearTimeout);
    playing = [];
    root.classList.add("pp-building");
    keys.forEach(function (k, i) {
      playing.push(setTimeout(function () { groups[k].forEach(function (e) { e.classList.add("pp-on"); }); }, 300 + i * 380));
    });
    playing.push(setTimeout(function () {
      root.classList.remove("pp-building");
      els.forEach(function (e) { e.classList.remove("pp-on"); });
      playing = null;
    }, 300 + keys.length * 380 + 700));
  }
  function playOnce() {
    var key = "pp-played:" + location.pathname, seen = false;
    try { seen = sessionStorage.getItem(key) === "1"; sessionStorage.setItem(key, "1"); } catch (e) {}
    var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!seen && !still) play();
  }

  /* 1 CSS mm per mm: the size the page prints at (as near as the screen allows) */
  function printSize() { zoomTo(1); }

  function buildUI() {
    ui = document.createElement("div");
    ui.className = "pp-ui";
    ui.innerHTML = '<button type="button" data-z="out" title="Zoom out (-)">−</button><span class="pp-zoom"></span>' +
      '<button type="button" data-z="in" title="Zoom in (+)">+</button><button type="button" data-z="fit" title="Fit (0)">Fit</button>' +
      '<button type="button" data-z="one" title="Print size (1)">1:1</button>' +
      '<button type="button" data-z="play" title="Play the builds (p)">▶</button>';
    document.body.appendChild(ui);
    zoomLabel = ui.querySelector(".pp-zoom");
    ui.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      var z = b.getAttribute("data-z");
      if (z === "in") zoomTo(scale * 1.25); else if (z === "out") zoomTo(scale / 1.25);
      else if (z === "fit") { fit(); window.dispatchEvent(new Event("resize")); }
      else if (z === "play") play(); else printSize();
    });
  }

  /* The zoom and scroll survive a reload (the review page reloads when the agent changes the poster). */
  var KEY = "pp-view:" + location.pathname;
  function save() {
    if (exportMode) return;
    try { sessionStorage.setItem(KEY, JSON.stringify({ s: scale, fit: fitting, x: view.scrollLeft, y: view.scrollTop })); } catch (e) {}
  }
  function restoreView() {
    var v = null;
    try { v = JSON.parse(sessionStorage.getItem(KEY) || "null"); } catch (e) {}
    if (!v || v.fit || !(v.s > 0)) return;
    fitting = false;
    apply(v.s);
    view.scrollLeft = v.x; view.scrollTop = v.y;
  }

  function init() {
    poster = document.querySelector(".pp-poster");
    view = document.querySelector(".pp-view");
    sizer = document.querySelector(".pp-sizer");
    if (!poster || !view || !sizer) return;
    if (!exportMode) buildUI();
    fit();
    if (!exportMode) {
      restoreView();
      window.addEventListener("beforeunload", save);
      view.addEventListener("scroll", function () { clearTimeout(view._t); view._t = setTimeout(save, 200); });
    }
    window.addEventListener("resize", function () { if (fitting) fit(); else apply(scale); });
    if (!exportMode) {
      view.addEventListener("wheel", function (e) {
        if (!e.ctrlKey && !e.metaKey) return;
        e.preventDefault();
        zoomTo(scale * Math.exp(-e.deltaY * 0.0022), e.clientX, e.clientY);
      }, { passive: false });
      document.addEventListener("keydown", function (e) {
        if (e.target.closest && e.target.closest("input, textarea, select, [contenteditable]")) return;
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomTo(scale * 1.25); }
        else if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomTo(scale / 1.25); }
        else if (e.key === "0" || e.key === "f" || e.key === "F") { e.preventDefault(); fit(); window.dispatchEvent(new Event("resize")); }
        else if (e.key === "1") { e.preventDefault(); printSize(); }
        else if (e.key === "p" || e.key === "P") { e.preventDefault(); play(); }
      });
    }
  }

  var mathDone = new Promise(function (res) {
    var tries = 0;
    (function wait() {
      var MJ = window.MathJax;
      // typesetPromise appears once MathJax has started; only then is startup.promise the one that ends with the typesetting
      if (MJ && MJ.typesetPromise && MJ.startup && MJ.startup.promise) {
        MJ.startup.promise.then(function () { return MJ.typesetPromise(); }).then(res, res);
        return;
      }
      if (!document.querySelector("script[src*='mathjax']") || ++tries > 200) { res(); return; }
      setTimeout(wait, 50);
    })();
  });
  var ready = Promise.all([
    new Promise(function (res) { if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", res); else res(); }),
    document.fonts ? document.fonts.ready : Promise.resolve(),
    mathDone
  ]).then(function () {
    if (!poster) init();
    if (fitting) fit(); else apply(scale);
    root.setAttribute("data-pp-ready", "1");
    playOnce();
  });

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.Poster = { cfg: cfg, width_mm: W, height_mm: H, fit: fit, zoom: zoomTo, ready: ready, play: play,
                    get scale() { return scale; } };
})();
