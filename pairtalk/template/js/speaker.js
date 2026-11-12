// Derived from html-slide by Yanwei Sun (https://github.com/Yanwei-Sun/html-slide); see NOTICE.md.
// Speaker view: a second window with the current slide, the next click, the script, and a timer, kept in step with the
// window the audience sees. V (or Speaker view in the M menu) opens it. Drag it to your own screen, then make the audience
// window full screen on the projector (F). Drive the talk from either window: moves and builds, B (blank the audience
// screen), and clicks on a slide's buttons and sliders reach both. The windows talk through postMessage, so a bundled deck
// opened as a file works too. window.DECK_MINUTES (say 15) gives the timer a target and a pace bar.
//   index.html            the audience window
//   index.html?speaker    the speaker window; V there opens the audience window if none is connected
//   index.html?preview    the next-click preview inside the speaker window
(function () {
  const q = new URLSearchParams(location.search);
  const role = q.has('preview') ? 'preview' : q.has('speaker') ? 'speaker' : 'audience';
  const B = document.body, TAG = 'deckSpeaker';
  const $ = s => document.querySelector(s);
  const ours = e => (e.origin === location.origin || location.protocol === 'file:') && e.data && e.data[TAG] === 1;
  const ready = fn => (function wait() { if (window.Deck && Deck.ready) { if (!B.classList.contains('print')) fn(); } else setTimeout(wait, 50); })();
  const nameOf = s => (s.name || s.title || (s.kind === 'title' ? 'Title' : s.id) || '').replace(/<[^>]+>/g, '');
  const nextOf = (i, k) => k < (Deck.slides[i].steps || 0) ? { i, k: k + 1 } : i + 1 < Deck.slides.length ? { i: i + 1, k: 0 } : null;
  const at = (i, k) => '#' + (i + 1) + (k ? '.' + k : '');

  // ---------- the preview: shows whatever click the speaker window asks for ----------
  if (role === 'preview') {
    B.classList.add('speaker-preview');
    let want = null;
    const apply = () => { if (want && Deck.ready && (want.i !== Deck.cur || want.k !== Deck.step)) Deck.go(want.i, want.k, false); };
    addEventListener('message', e => { if (e.source === parent && ours(e) && e.data.t === 'show') { want = e.data; apply(); } });
    ready(() => { apply(); parent.postMessage({ [TAG]: 1, t: 'ready' }, '*'); });
    return;
  }
  if (role === 'speaker') B.classList.add('speaker-view');   // before the engine first fits the stage

  // ---------- the link between the two windows ----------
  let peer = role === 'speaker' ? window.opener : null;   // the audience learns its speaker window from the first ping
  let synced = false, remote = false, lastPong = 0, blankOn = false;
  let ui = null, frame = null, frameReady = false, tm = null;   // the speaker window's parts; tm = { t0, paused } for the timer
  const send = m => { if (peer && !peer.closed) try { peer.postMessage(Object.assign({ [TAG]: 1 }, m), '*'); } catch (e) {} };
  const quiet = fn => { remote = true; try { fn(); } finally { remote = false; } };   // apply a move without sending it back
  const state = () => ({ t: 'state', i: Deck.cur, k: Deck.step, blank: blankOn });
  function openOther() {
    if (peer && !peer.closed) { peer.focus(); return; }
    const u = new URL(location.href);
    if (role === 'audience') u.searchParams.set('speaker', '1'); else u.searchParams.delete('speaker');
    u.hash = at(Deck.cur, Deck.step);
    peer = role === 'audience' ? window.open(u.href, 'deck-speaker', 'width=1500,height=900') : window.open(u.href, 'deck-audience');
    synced = true;   // the new window takes this one's place in the talk
  }
  function setBlank(on) {
    blankOn = !!on;
    if (role === 'audience') $('#blank').classList.toggle('on', blankOn);
    else { const b = $('#speaker .bl'); if (b) b.classList.toggle('on', blankOn); }
  }

  // controls on a slide are matched by their place among the slide's controls, the same in every window
  const CTL = 'button, [role="button"]', FIELD = 'input, select, textarea';
  const locate = (n, sel) => {
    const i = Deck.slides.findIndex(s => s.el.contains(n));
    return i < 0 ? null : { i, n: Array.from(Deck.slides[i].el.querySelectorAll(sel)).indexOf(n) };
  };
  const control = (m, sel) => { const s = Deck.slides[m.i]; return s && s.el.querySelectorAll(sel)[m.n]; };

  addEventListener('keydown', e => {
    if (!window.Deck || !Deck.ready || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.target && e.target.closest && e.target.closest('textarea, input, [contenteditable="true"]')) return;
    if (e.key === 'v' || e.key === 'V') { e.preventDefault(); e.stopImmediatePropagation(); openOther(); return; }
    if (role !== 'speaker') return;
    // in the speaker window, B blanks the audience screen, not yours
    if (e.key === 'b' || e.key === 'B') { e.preventDefault(); e.stopImmediatePropagation(); setBlank(!blankOn); send({ t: 'blank', on: blankOn }); }
    if (e.key === 'Escape' && blankOn) { setBlank(false); send({ t: 'blank', on: false }); }
  }, true);

  ready(() => {
    const D = Deck, go = D.go, next = D.next;
    D.go = function (i, k, a) {
      const r = go.apply(this, arguments);
      if (!remote) send({ t: 'go', i: D.cur, k: D.step, a });
      if (role === 'speaker') update();
      return r;
    };
    D.next = function () { if (D.busy && !remote) send({ t: 'skip' }); return next.apply(this, arguments); };   // a click that only finishes an animation

    addEventListener('message', e => {
      if (!ours(e)) return;
      const m = e.data;
      if (role === 'speaker' && frame && e.source === frame.contentWindow) { if (m.t === 'ready') { frameReady = true; update(); } return; }
      if (e.source !== peer) {
        if (role !== 'audience' || (peer && !peer.closed) || m.t !== 'ping') return;
        peer = e.source;
      }
      if (role === 'speaker') lastPong = Date.now();   // any word from the audience window shows it is there
      switch (m.t) {
        case 'ping': send({ t: 'pong' }); if (!synced) send({ t: 'hello' }); break;   // a reloaded audience window asks where the talk is
        case 'pong': lastPong = Date.now(); break;
        case 'hello': if (role === 'speaker' || synced) send(state()); else send({ t: 'hello' }); break;
        case 'state': if (!synced) { synced = true; quiet(() => D.go(m.i, m.k, false)); setBlank(m.blank); } break;
        case 'go': synced = true; quiet(() => D.go(m.i, m.k, m.a)); break;
        case 'skip': if (D.busy) D.busy.skip = true; break;
        case 'blank': setBlank(m.on); break;
        case 'ctl': { const c = control(m, CTL); if (c) quiet(() => c.click()); break; }
        case 'field': {
          const f = control(m, FIELD); if (!f) break;
          if (f.type === 'checkbox' || f.type === 'radio') f.checked = m.c; else f.value = m.v;
          f.dispatchEvent(new Event(m.type, { bubbles: true }));
          break;
        }
      }
    });

    // clicks on a slide's buttons, and its sliders and fields, happen in both windows (only real input is sent on)
    document.addEventListener('click', e => {
      const c = e.isTrusted && e.target.closest && e.target.closest(CTL);
      const w = c && $('#stage').contains(c) && locate(c, CTL);
      if (w) send({ t: 'ctl', i: w.i, n: w.n });
    }, true);
    ['input', 'change'].forEach(type => document.addEventListener(type, e => {
      const f = e.target;
      if (!e.isTrusted || !f.matches || !f.matches(FIELD) || !$('#stage').contains(f)) return;
      const w = locate(f, FIELD);
      if (w) send({ t: 'field', i: w.i, n: w.n, type, v: f.value, c: f.checked });
    }, true));

    const btn = document.createElement('button');
    btn.dataset.a = 'speaker'; btn.type = 'button'; btn.textContent = role === 'audience' ? 'Speaker view' : 'Audience window';
    btn.addEventListener('click', e => { e.stopPropagation(); openOther(); });
    $('#bar').appendChild(btn);
    const h = $('#pres-handle'); if (h) h.title += role === 'audience' ? ' · Speaker view (V)' : ' · Audience window (V)';

    if (role === 'audience') {
      new MutationObserver(() => { blankOn = $('#blank').classList.contains('on'); send({ t: 'blank', on: blankOn }); })
        .observe($('#blank'), { attributes: true, attributeFilter: ['class'] });
      return;
    }
    build();
    send({ t: 'hello' }); send({ t: 'ping' });
    setInterval(() => send({ t: 'ping' }), 1000);
  });

  // ---------- the speaker window ----------
  const TK = 'deck-speaker-timer:' + location.pathname;   // t0: when the timer started; paused: when it was paused, 0 while running
  const saveTimer = () => { try { sessionStorage.setItem(TK, JSON.stringify(tm)); } catch (e) {} };
  const mmss = s => { s = Math.max(0, Math.floor(s)); return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0'); };

  function build() {
    document.title = 'Speaker view · ' + document.title;
    ui = document.createElement('div'); ui.id = 'speaker';
    ui.innerHTML = '<div class="cap now"></div><div class="cap nxt"></div>'
      + '<div class="pv"><iframe tabindex="-1" aria-hidden="true" title="Next click"></iframe><div class="end">End of the slides</div></div>'
      + '<div class="clock"><div class="tm"><span class="el">00:00</span><span class="of"></span></div>'
      + '<div class="pace" title="Gold: time used. Blue tick: how far through the main slides you are."><i></i><b></b></div>'
      + '<div class="row"><button type="button" data-k="pause">Pause</button><button type="button" data-k="reset">Reset</button><span class="wall"></span></div>'
      + '<div class="link"></div><div class="bl">Audience screen blanked (B)</div></div>';
    B.appendChild(ui);
    ui.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      e.stopPropagation(); setTimeout(() => b.blur(), 0);   // Space keeps advancing the talk
      const now = Date.now();
      if (b.dataset.k === 'pause') { if (tm.paused) { tm.t0 += now - tm.paused; tm.paused = 0; } else tm.paused = now; }
      if (b.dataset.k === 'reset') tm = { t0: now, paused: tm.paused ? now : 0 };
      saveTimer(); tick();
    });
    const u = new URL(location.href); u.searchParams.delete('speaker'); u.searchParams.set('preview', '1');
    const n = nextOf(Deck.cur, Deck.step); u.hash = n ? at(n.i, n.k) : '';
    frame = ui.querySelector('iframe'); frame.src = u.href;
    try { tm = JSON.parse(sessionStorage.getItem(TK)); } catch (e) {}   // a reload keeps the timer running
    if (!tm || !tm.t0) { tm = { t0: Date.now(), paused: 0 }; saveTimer(); }
    const sb = $('#bar [data-a="script"]'); if (sb && !$('#script').classList.contains('on')) sb.click();   // the script, always on here
    new MutationObserver(fitNote).observe($('#script'), { childList: true }); addEventListener('resize', fitNote); fitNote();
    if (document.fonts) document.fonts.addEventListener('loadingdone', fitNote);   // the script's font may load only now
    dispatchEvent(new Event('resize'));
    update(); tick(); setInterval(tick, 250);
  }

  // the current note at the largest size, 28px down to 19px, that fits the script column without scrolling
  function fitNote() {
    const p = $('#script'), c = p && p.querySelector('.sn.cur');
    if (!c || c.querySelector('textarea')) return;
    const room = p.clientHeight - Math.min(c.offsetTop, 96) - 64;   // the engine scrolls a note up to 96px from the top; keep "next:" in view
    for (let f = 28; f >= 19; f--) { c.style.fontSize = f + 'px'; if (c.offsetHeight <= room) break; }
  }

  function update() {
    if (!ui) return;
    const s = Deck.slides[Deck.cur], main = Deck.slides.filter(x => !x.backup).length, n = nextOf(Deck.cur, Deck.step);
    ui.querySelector('.cap.now').textContent = (s.backup ? 'Backup slide ' + s.label : 'Slide ' + s.label + ' of ' + main)
      + (s.steps ? ' · click ' + Deck.step + ' of ' + s.steps : '');
    const ns = n && Deck.slides[n.i];
    ui.querySelector('.cap.nxt').textContent = !n ? 'Next' : n.i === Deck.cur ? 'Next: click ' + n.k + ' of ' + s.steps
      : 'Next: ' + (ns.backup ? 'backup ' : 'slide ') + ns.label + ' · ' + nameOf(ns);
    ui.querySelector('.pv').classList.toggle('done', !n);
    if (n && frameReady) frame.contentWindow.postMessage({ [TAG]: 1, t: 'show', i: n.i, k: n.k }, '*');
  }

  function tick() {
    if (!ui) return;
    const t = ((tm.paused || Date.now()) - tm.t0) / 1000, goal = (+window.DECK_MINUTES || 0) * 60;
    const box = ui.querySelector('.tm');
    box.querySelector('.el').textContent = mmss(t);
    box.querySelector('.of').textContent = goal ? ' / ' + mmss(goal) : '';
    ui.querySelector('.wall').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    box.classList.toggle('warn', goal > 0 && t > goal - 120 && t <= goal);
    box.classList.toggle('over', goal > 0 && t > goal);
    box.classList.toggle('paused', !!tm.paused);
    ui.querySelector('[data-k="pause"]').textContent = tm.paused ? 'Resume' : 'Pause';
    const pace = ui.querySelector('.pace'), s = Deck.slides[Deck.cur], main = Deck.slides.filter(x => !x.backup).length;
    pace.style.display = goal ? '' : 'none';
    if (goal) {
      pace.querySelector('i').style.width = Math.min(100, 100 * t / goal) + '%';
      const mark = pace.querySelector('b');
      mark.style.display = s.backup ? 'none' : '';
      mark.style.left = 100 * (Deck.cur + (s.steps ? Deck.step / (s.steps + 1) : 0)) / main + '%';
    }
    const on = peer && !peer.closed && Date.now() - lastPong < 2500, link = ui.querySelector('.link');
    link.classList.toggle('on', !!on);
    link.textContent = on ? '● Audience window connected' : '○ No audience window: press V to open one';
  }
})();
