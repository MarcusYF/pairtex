/* PairDeck review overlay: comment on a slide by dragging a box over it.
   `pairdeck review` injects this into the pages it serves; it is never written into the deck.
   Comments go to POST /__pairdeck/comments; replies written by `pairdeck resolve` come back through GET /__pairdeck/state. */
(function () {
  "use strict";
  var CFG = window.PAIRDECK || {};
  var UNIT = CFG.unit === "poster" ? "poster" : "slide", TOOL = CFG.tool || "PairDeck", CLI = CFG.cli || "pairdeck";
  var API = "/__pairdeck/";
  var POLL_MS = 2500, MIN_DRAG = 8;
  var comments = [], sig = null, isOpen = false, marking = null, draft = null, shownId = null, tab = "slide", busy = false;
  var panel, fab, countBtn, layer, list, compose, area, where, msg;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function allSlides() { return Array.prototype.slice.call(document.querySelectorAll(".dk-slide")); }
  function deckEl() { return $(".dk-deck") || document.body; }
  function distinct(nodes) {
    var seen = {};
    Array.prototype.forEach.call(nodes, function (e) { seen[e.getAttribute("data-step")] = 1; });
    return Object.keys(seen).length;
  }
  function here() {
    var slides = allSlides(), i = window.Deck ? window.Deck.index : 0, s = slides[i] || null;
    var h = s && s.querySelector(".dk-h");
    return {
      slide: i + 1, el: s,
      step: s ? distinct(s.querySelectorAll("[data-step].is-on")) : 0,
      steps: s ? distinct(s.querySelectorAll("[data-step]")) : 0,
      label: s ? (s.getAttribute("data-label") || "") : "",
      title: h ? h.textContent.replace(/\s+/g, " ").trim() : "",
      id: s ? (s.id || "") : ""
    };
  }
  /* Boxes are stored as fractions of the slide's content block (.dk-inner), so they land on the same content at any
     window size; without the engine, of the deck area. */
  function frame(slideEl) {
    var inner = slideEl && slideEl.querySelector(".dk-inner");
    return (inner || deckEl()).getBoundingClientRect();
  }
  /* A box is also stored relative to the smallest block under its centre (a figure, the headline, the takeaway...), so it
     lands on the same marks when the layout reflows (a narrower window, a phone, the panel opening). */
  var ANCHORS = CFG.anchors || ".dk-fig, .dk-h, .dk-take, .dk-note, .dk-list, .dk-ctl, .dk-cols, .dk-sub";
  function anchorFor(slideEl, r) {
    if (!slideEl) return null;
    var cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2, best = null;
    slideEl.querySelectorAll(ANCHORS).forEach(function (el, i) {
      var b = el.getBoundingClientRect();
      if (cx < b.left || cx > b.right || cy < b.top || cy > b.bottom || !b.width || !b.height) return;
      if (!best || b.width * b.height < best.area) best = { i: i, area: b.width * b.height, b: b };
    });
    if (!best) return null;
    var B = best.b;
    return { i: best.i, x: (r.left - B.left) / B.width, y: (r.top - B.top) / B.height, w: (r.right - r.left) / B.width,
             h: (r.bottom - r.top) / B.height };
  }
  function boxRect(c, slideEl) {
    var a = c.anchor, els = slideEl ? slideEl.querySelectorAll(ANCHORS) : [];
    if (a && els[a.i]) {
      var B = els[a.i].getBoundingClientRect();
      if (B.width && B.height) return { left: B.left + a.x * B.width, top: B.top + a.y * B.height, width: a.w * B.width, height: a.h * B.height };
    }
    var F = frame(slideEl);
    return { left: F.left + c.box.x * F.width, top: F.top + c.box.y * F.height, width: c.box.w * F.width, height: c.box.h * F.height };
  }
  function when(t) {
    var d = new Date(t);
    if (isNaN(d)) return "";
    var same = d.toDateString() === new Date().toDateString();
    return same ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  }
  function shownInSlide(el, stop) {
    for (var e = el; e && e !== stop; e = e.parentNode) {
      if (e.nodeType !== 1) continue;
      var cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) < 0.05) return false;
    }
    return true;
  }
  /* The words under a box, so the agent knows what it covers even if the layout moves. */
  function textUnder(slideEl, r) {
    if (!slideEl) return "";
    var out = [], seen = {};
    slideEl.querySelectorAll("text, h1, h2, h3, p, li, td, th, figcaption, button, label, .pp-t, .pp-n, .pp-k, .pp-lead").forEach(function (el) {
      if (!shownInSlide(el, slideEl)) return;
      if (el.tagName.toLowerCase() !== "text" && el.closest("svg")) return;
      var b = el.getBoundingClientRect(), cx = (b.left + b.right) / 2, cy = (b.top + b.bottom) / 2;
      if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom) return;
      var t = el.textContent.replace(/\s+/g, " ").trim();
      if (t && !seen[t]) { seen[t] = 1; out.push(t); }
    });
    var s = out.join(" · ");
    return s.length > 300 ? s.slice(0, 298) + "…" : s;
  }

  /* The named part of the page under a box (the smallest element with a data-label, other than the slide itself):
     on a poster, the block a comment is about. */
  function blockUnder(slideEl, r) {
    if (!slideEl) return "";
    var cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2, best = null;
    slideEl.querySelectorAll("[data-label]").forEach(function (el) {
      var b = el.getBoundingClientRect();
      if (cx < b.left || cx > b.right || cy < b.top || cy > b.bottom || !b.width || !b.height) return;
      if (!best || b.width * b.height < best.area) best = { area: b.width * b.height, label: el.getAttribute("data-label") };
    });
    return best ? best.label : "";
  }

  // ------------------------------------------------------------------ building the UI

  function build() {
    fab = document.createElement("button");
    fab.type = "button";
    fab.className = "pd-fab";
    fab.title = "Comment on this " + UNIT + " (c)";
    fab.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8A2.5 2.5 0 0 1 17.5 16H10l-5 4v-4.3A2.5 2.5 0 0 1 4 13.5z"/><path d="M12 6.5v6M9 9.5h6"/></svg><span>Comment</span>';
    countBtn = document.createElement("button");
    countBtn.type = "button";
    countBtn.className = "pd-count";
    countBtn.title = "Show comments";
    panel = document.createElement("aside");
    panel.className = "pd-panel";
    panel.setAttribute("aria-label", "Comments");
    panel.innerHTML =
      '<header class="pd-head"><b>Comments</b><span class="pd-tabs" role="group" aria-label="Which comments">' +
      '<button type="button" data-tab="slide">This slide</button><button type="button" data-tab="all">All</button></span>' +
      '<button type="button" class="pd-x" aria-label="Close comments">×</button></header>' +
      '<div class="pd-compose" hidden><div class="pd-where"></div>' +
      '<textarea rows="4" placeholder="What should change? For example: too many words; make the second bar teal."></textarea>' +
      '<div class="pd-row"><button type="button" class="pd-send">Send</button><button type="button" class="pd-cancel">Cancel</button>' +
      '<button type="button" class="pd-redraw">Redraw box</button></div><div class="pd-msg" aria-live="polite"></div></div>' +
      '<div class="pd-list"></div>' +
      '<footer class="pd-foot">Your comments go to ' + esc(CFG.agent || "the agent") + ' through ' + esc(TOOL) + '. ' +
      'Press c to comment, Esc to cancel, Ctrl or ⌘ + Enter to send.</footer>';
    layer = document.createElement("div");
    layer.className = "pd-layer";
    document.body.append(layer, fab, countBtn, panel);
    list = $(".pd-list", panel);
    compose = $(".pd-compose", panel);
    area = $("textarea", panel);
    where = $(".pd-where", panel);
    msg = $(".pd-msg", panel);

    fab.addEventListener("click", function () { startMark(null); });
    countBtn.addEventListener("click", function () { setOpen(!isOpen); });
    $(".pd-x", panel).addEventListener("click", function () { setOpen(false); });
    $(".pd-send", panel).addEventListener("click", send);
    $(".pd-cancel", panel).addEventListener("click", cancelDraft);
    $(".pd-redraw", panel).addEventListener("click", function () { startMark(draft && draft.parent); });
    panel.querySelectorAll("[data-tab]").forEach(function (b) {
      b.addEventListener("click", function () { tab = b.getAttribute("data-tab"); render(); });
    });
    area.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); send(); }
      if (e.key === "Escape") { e.preventDefault(); cancelDraft(); }
    });
    // Keys inside the panel (Enter or Space on a button) must not also step the deck.
    panel.addEventListener("keydown", function (e) { e.stopPropagation(); });
    list.addEventListener("click", onListClick);
    document.addEventListener("keydown", function (e) {
      if (e.target.closest && e.target.closest("input, textarea, select, [contenteditable]")) return;
      if (e.key === "Escape" && marking) { e.preventDefault(); endMark(); return; }
      if ((e.key === "c" || e.key === "C") && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); startMark(null); }
    });
    window.addEventListener("resize", drawBoxes);
    document.addEventListener("scroll", drawBoxes, true); // a tall slide scrolls: boxes follow its content
    if (window.Deck && window.Deck.on) window.Deck.on("step", function () { render(); });
  }

  function setOpen(v) {
    isOpen = v;
    document.body.classList.toggle("pd-open", v);
    panel.classList.toggle("is-open", v);
    window.dispatchEvent(new Event("resize")); // the engine refits figures to the narrower deck
    render();
  }

  // ------------------------------------------------------------------ marking a box

  function startMark(parent) {
    if (marking) return;
    if (!isOpen) setOpen(true);
    var ov = document.createElement("div");
    ov.className = "pd-mark";
    ov.innerHTML = '<div class="pd-mhint">Drag a box over what you mean · click for the whole ' + UNIT + ' · Esc cancels</div>';
    var R = deckEl().getBoundingClientRect();
    ov.style.left = R.left + "px"; ov.style.top = R.top + "px"; ov.style.width = R.width + "px"; ov.style.height = R.height + "px";
    document.body.append(ov);
    marking = { ov: ov, box: null, x0: 0, y0: 0, down: false, parent: parent };
    clearBoxes();
    ov.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      e.preventDefault();
      try { ov.setPointerCapture(e.pointerId); } catch (_) {}
      marking.down = true; marking.x0 = e.clientX; marking.y0 = e.clientY;
      marking.box = document.createElement("div");
      marking.box.className = "pd-box draft";
      layer.append(marking.box);
      size(e);
    });
    ov.addEventListener("pointermove", function (e) { if (marking && marking.down) size(e); });
    ov.addEventListener("pointerup", function (e) {
      if (!marking || !marking.down) return;
      marking.down = false;
      var r = size(e), h = here(), F = frame(h.el), box = null, anchor = null, under = "", block = "";
      if (r.w >= MIN_DRAG && r.h >= MIN_DRAG) {
        var sr = { left: r.x, top: r.y, right: r.x + r.w, bottom: r.y + r.h };
        box = { x: (r.x - F.left) / F.width, y: (r.y - F.top) / F.height, w: r.w / F.width, h: r.h / F.height };
        anchor = anchorFor(h.el, sr);
        under = textUnder(h.el, sr);
        block = blockUnder(h.el, sr);
      }
      var parent = marking.parent;
      endMark();
      openDraft(h, box, under, parent, anchor, block);
    });
    ov.addEventListener("click", function (e) { e.stopPropagation(); });
  }
  function size(e) {
    var x = Math.min(marking.x0, e.clientX), y = Math.min(marking.y0, e.clientY);
    var r = { x: x, y: y, w: Math.abs(e.clientX - marking.x0), h: Math.abs(e.clientY - marking.y0) };
    var s = marking.box.style;
    s.left = r.x + "px"; s.top = r.y + "px"; s.width = r.w + "px"; s.height = r.h + "px";
    return r;
  }
  function endMark() {
    if (!marking) return;
    if (marking.box) marking.box.remove();
    marking.ov.remove();
    marking = null;
    drawBoxes();
  }

  // ------------------------------------------------------------------ the draft

  function openDraft(h, box, under, parent, anchor, block) {
    var keep = draft ? area.value : "";
    draft = { slide: h.slide, slide_id: h.id, label: h.label, title: h.title, step: h.step, steps: h.steps, box: box,
              anchor: anchor || null, under: under, block: block || "", parent: parent || null,
              viewport: [window.innerWidth, window.innerHeight] };
    compose.hidden = false;
    var place = UNIT === "poster" ? (block ? "<b>" + esc(block) + "</b>" : "the poster")
      : "slide " + h.slide + (h.steps ? ", step " + h.step + " of " + h.steps : "");
    where.innerHTML = (parent ? "Follow-up to <b>" + esc(parent) + "</b> · " : "New comment · ") + place +
      " · " + (box ? "the box" : "the whole " + UNIT) +
      (under ? '<span class="pd-under">' + esc(under) + "</span>" : "");
    area.value = keep;
    msg.textContent = "";
    render();
    area.focus();
  }
  function cancelDraft() {
    draft = null;
    compose.hidden = true;
    area.value = "";
    msg.textContent = "";
    render();
  }
  function send() {
    if (!draft || busy) return;
    var text = area.value.trim();
    if (!text) { msg.textContent = "Type the comment first."; area.focus(); return; }
    busy = true;
    msg.textContent = "Sending…";
    var body = Object.assign({}, draft, { text: text });
    fetch(API + "comments", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || r.status); return j; }); })
      .then(function (rec) {
        draft = null;
        compose.hidden = true;
        area.value = "";
        msg.textContent = "";
        shownId = rec.id;
        return poll();
      })
      .catch(function (e) { msg.textContent = "Not sent: " + e.message + ". Is `" + CLI + " review` still running?"; })
      .then(function () { busy = false; });
  }

  // ------------------------------------------------------------------ the list and the boxes

  function statusChip(c) {
    var cls = { "waiting": "st-wait", "with the agent": "st-agent", "answered": "st-done", "kept": "st-kept" }[c.status] || "";
    return '<span class="pd-chip ' + cls + '">' + esc(c.status) + "</span>";
  }
  function itemHTML(c) {
    var replies = (c.replies || []).map(function (r) {
      return '<div class="pd-reply"><b>' + esc(r.agent || CFG.agent || "Agent") + ":</b> " + esc(r.text) + "</div>";
    }).join("");
    var acts = c.replies && c.replies.length
      ? '<div class="pd-actions">' + (c.kept ? "" : '<button type="button" data-act="keep" title="Accept the change as made">Keep</button>') +
        '<button type="button" data-act="follow">Follow up</button></div>' : "";
    return '<article class="pd-item' + (c.id === shownId ? " is-shown" : "") + '" data-id="' + esc(c.id) + '">' +
      '<div class="pd-meta"><b>' + esc(c.id) + "</b> · " + (UNIT === "poster" ? esc(c.block || "poster")
        : "slide " + c.slide + (c.steps ? "." + c.step : "")) +
      (c.parent ? " · re " + esc(c.parent) : "") + " · " + esc(when(c.time)) + " " + statusChip(c) + "</div>" +
      '<div class="pd-text"><b>' + esc(c.author || CFG.author || "You") + ":</b> " + esc(c.text) + "</div>" + replies + acts +
      "</article>";
  }
  function render() {
    if (!panel) return;
    var h = here();
    var mine = comments.filter(function (c) { return c.slide === h.slide; });
    var rows = tab === "all" ? comments : mine;
    panel.querySelectorAll("[data-tab]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-tab") === tab)); });
    $("[data-tab=slide]", panel).textContent = "This " + UNIT + " (" + mine.length + ")";
    $(".pd-tabs", panel).hidden = allSlides().length <= 1;  // one page (a poster): "this slide" and "all" are the same
    $("[data-tab=all]", panel).textContent = "All (" + comments.length + ")";
    list.innerHTML = rows.length ? rows.slice().reverse().map(itemHTML).join("")
      : '<p class="pd-empty">' + (tab === "all" ? "No comments yet." : "No comments on this " + UNIT + " yet.") +
        " Press <b>Comment</b>, drag a box over what you mean, and type.</p>";
    var open = comments.filter(function (c) { return c.status !== "answered" && c.status !== "kept"; }).length;
    countBtn.textContent = comments.length ? comments.length + (open ? " · " + open + " open" : "") : "0";
    countBtn.hidden = !comments.length && !isOpen;
    drawBoxes();
  }
  function clearBoxes() { layer.querySelectorAll(".pd-box:not(.draft)").forEach(function (b) { b.remove(); }); }
  function putBox(c, cls, label) {
    var h = here();
    if (!c.box || c.slide !== h.slide) return;
    var R = boxRect(c, h.el), b = document.createElement("div");
    b.className = "pd-box " + cls;
    b.style.left = R.left + "px";
    b.style.top = R.top + "px";
    b.style.width = R.width + "px";
    b.style.height = R.height + "px";
    if (label) { var t = document.createElement("span"); t.textContent = label; b.append(t); }
    layer.append(b);
  }
  function drawBoxes() {
    if (!layer) return;
    clearBoxes();
    if (!isOpen || marking) return;
    var h = here();
    comments.forEach(function (c) {
      // A comment the author accepted (Keep) is settled: its box leaves the slide, and comes back only while
      // the author has that comment selected in the list.
      if (c.status === "kept" && c.id !== shownId) return;
      if (c.slide === h.slide && c.box) putBox(c, c.id === shownId ? "shown" : "faint", c.id);
    });
    if (draft && draft.box && draft.slide === h.slide) putBox(draft, "pending", "new");
  }
  function goTo(c) {
    var h = here();
    if (window.Deck && (h.slide !== c.slide || h.step !== (c.step || 0))) {
      window.Deck.go(c.slide - 1);
      for (var k = 0; k < (c.step || 0); k++) window.Deck.next();
    }
    var s = allSlides()[c.slide - 1], els = s ? s.querySelectorAll(ANCHORS) : [];
    if (c.anchor && els[c.anchor.i] && els[c.anchor.i].scrollIntoView) els[c.anchor.i].scrollIntoView({ block: "nearest" });
  }
  function onListClick(e) {
    var item = e.target.closest(".pd-item");
    if (!item) return;
    var c = comments.filter(function (x) { return x.id === item.getAttribute("data-id"); })[0];
    if (!c) return;
    var act = e.target.closest("[data-act]");
    if (act && act.getAttribute("data-act") === "keep") {
      fetch(API + "keep", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: c.id }) })
        .then(poll);
      return;
    }
    shownId = c.id;
    goTo(c);
    if (act && act.getAttribute("data-act") === "follow") {
      var h = here();
      openDraft(h, c.box, c.under || "", c.id, c.anchor, c.block);
      return;
    }
    setTimeout(render, 80);
  }

  // ------------------------------------------------------------------ polling and reloads

  function poll() {
    return fetch(API + "state", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (s) {
      comments = s.comments || [];
      if (sig && s.sig !== sig && !draft && !marking) {
        // The deck changed on disk (the agent's fix): reload, keeping the slide, the step and the panel.
        try {
          var h = here();
          sessionStorage.setItem("pd-restore", JSON.stringify({ slide: h.slide, step: h.step, open: isOpen, tab: tab, shown: shownId }));
        } catch (_) {}
        location.reload();
        return;
      }
      sig = s.sig;
      render();
    }).catch(function () {});
  }

  function restore() {
    var want = null;
    try { want = JSON.parse(sessionStorage.getItem("pd-restore") || "null"); sessionStorage.removeItem("pd-restore"); } catch (_) {}
    var q = /[?&]comment=([\w-]+)/.exec(location.search);
    return poll().then(function () {
      if (q) {
        var c = comments.filter(function (x) { return x.id === q[1]; })[0];
        if (c) { shownId = c.id; tab = "slide"; goTo(c); setOpen(true); }
      } else if (want) {
        tab = want.tab || "slide";
        shownId = want.shown || null;
        if (window.Deck) goTo({ slide: want.slide, step: want.step });
        if (want.open) setOpen(true);
      }
      render();
    });
  }

  function start() {
    build();
    render();
    // After the engine has shown its first slide (it does so on load).
    setTimeout(function () { restore().then(function () { setInterval(poll, POLL_MS); }); }, 60);
  }
  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
