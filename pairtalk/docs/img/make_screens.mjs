#!/usr/bin/env node
// Make the README's screenshots from the demo talk: a slide, the speaker view, and a comment with a marked box and its reply.
// It sets up a throwaway data home, makes the demo talk, starts `pairtalk serve`, sends one comment through the review
// server's API (as the browser would), answers it with `pairtalk resolve`, and drives an installed Chrome with Playwright.
// Run: node docs/img/make_screens.mjs   (needs `npm install` and Chrome; CHROME_PATH if Chrome is elsewhere)
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP = path.resolve(HERE, '..', '..');
const PT = path.join(APP, 'bin', 'pairtalk');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'pairtalk-screens-'));
const env = { ...process.env, HOME: path.join(TMP, 'home'), PAIRTALK_HOME: path.join(TMP, 'data') };
fs.mkdirSync(env.HOME, { recursive: true });
const pt = (...args) => execFileSync('python3', [PT, ...args], { env, encoding: 'utf8' });
const CHROME = process.env.CHROME_PATH || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium']
  .find(p => fs.existsSync(p));

pt('setup', '--name', 'Ada Lovelace');
pt('new', 'pagerank', '--example', 'pagerank', '--dir', path.join(TMP, 'pagerank'));
const port = 8797, base = `http://127.0.0.1:${port}`;
const server = spawn('python3', [PT, 'serve', 'pagerank', '--port', String(port)], { env, stdio: 'ignore' });
const browser = await chromium.launch({ executablePath: CHROME });
try {
  for (let i = 0; i < 50; i++) { try { await fetch(base + '/'); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
  const post = body => fetch(base + '/__comments', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: base }, body: JSON.stringify(body) }).then(r => r.json());
  const c = await post({ deck: 'pagerank', n: 8, k: 2, sid: 'CONVERGE', title: 'The error shrinks geometrically', author: 'Grace Hopper',
    text: 'What does the dashed line guarantee? Say it in words next to the line.', box: { x: 1540, y: 380, w: 370, h: 130 } });
  pt('resolve', 'pagerank', c.cid, 'Labelled it "guarantee 0.85^t: the error shrinks at least this fast"; the script says why the measured line falls faster.');

  const shot = async (page, name, clip) => {
    const file = path.join(HERE, name);
    await page.screenshot({ path: file, clip });
    console.log(`${name}: ${(fs.statSync(file).size / 1024).toFixed(0)} KB`);
  };
  const ready = page => page.waitForFunction(() => window.Deck && Deck.ready && document.fonts.status === 'loaded');

  // 1. a slide, at its last click
  let page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
  await page.goto(base + '/#6.3'); await ready(page); await page.waitForTimeout(800);
  await shot(page, 'slide.png');

  await page.close();

  // 2. a comment with its marked box and the reply, in the comment panel
  page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
  await page.goto(base + '/#8.2'); await ready(page); await page.waitForTimeout(600);
  await page.keyboard.press('c'); await page.waitForTimeout(600);
  await page.click('#cmt .cbx'); await page.waitForTimeout(600);
  await page.mouse.move(700, 400);
  await shot(page, 'comment.png');
  await page.close();

  // 3. the speaker view: the slide, the next click, the script and the timer
  page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
  await page.goto(base + '/?speaker#4.1'); await ready(page); await page.waitForTimeout(1500);
  await page.mouse.move(10, 10);
  await shot(page, 'speaker.png');
  await page.close();
} finally {
  await browser.close();
  server.kill();
  fs.rmSync(TMP, { recursive: true, force: true });
}
