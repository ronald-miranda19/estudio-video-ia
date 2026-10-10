// Real screen recording of a web page for tutorials (Playwright + Chromium in Portuguese).
// Opens the page, waits, scrolls slowly to the bottom and back, and saves an MP4.
//   node ferramentas/gravar_tela.mjs URL saida.mp4 [LARGURA=1920] [ALTURA=1080] [SEGUNDOS=12]
// For clicks and typing, copy this file and write the steps in passos() — page.click('text=Entrar'), page.fill(...), etc.
// Always use example data, never real customers; blur internal addresses (localhost) and private data before delivering.
import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const [url, outArg, w = '1920', h = '1080', secs = '12'] = process.argv.slice(2);
if (!url || !outArg) { console.error('uso: node ferramentas/gravar_tela.mjs URL saida.mp4 [largura] [altura] [segundos]'); process.exit(1); }
const W = Number(w), H = Number(h), total = Number(secs) * 1000;
const dir = mkdtempSync(join(tmpdir(), 'gravacao-'));

async function passos(page) {
  // default tour: settle, scroll down slowly, come back up
  await page.waitForTimeout(1500);
  const height = await page.evaluate(() => document.body.scrollHeight);
  const steps = 60, down = (total - 3000) * 0.7 / steps;
  for (let i = 1; i <= steps; i++) {
    await page.evaluate((y) => window.scrollTo({ top: y }), (height - H) * (i / steps));
    await page.waitForTimeout(down);
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await page.waitForTimeout(1500);
}

let browser;
try { browser = await chromium.launch(); }
catch { browser = await chromium.launch({ channel: 'chrome' }); } // fallback: the installed Google Chrome
const ctx = await browser.newContext({ locale: 'pt-BR', viewport: { width: W, height: H }, recordVideo: { dir, size: { width: W, height: H } } });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await passos(page);
await ctx.close();
await browser.close();

const webm = readdirSync(dir).find((f) => f.endsWith('.webm'));
execFileSync('ffmpeg', ['-nostdin', '-y', '-loglevel', 'error', '-i', join(dir, webm), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', resolve(outArg)]);
rmSync(dir, { recursive: true, force: true });
console.log('pronto:', resolve(outArg));
