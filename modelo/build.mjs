// Builds index.html (scene slots + music + SFX) and the two full-length layers it mounts:
// compositions/fundo.html (shared background) and compositions/transicoes.html (wipe, flashes, end fade).
// The scenes live in compositions/s*.html. Run: node build.mjs
//
// To adapt: change FORMATO, DESTAQUE, the scene list (slots) and the effects list (sfx). Everything else follows.
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';

const FORMATO = 'deitado';    // 'deitado' = 1920x1080 (site, YouTube) | 'em-pe' = 1080x1920 (Reels, TikTok, Shorts)
const DESTAQUE = '#7c5cff';   // the one accent colour of the video
const DUR = 10;               // total seconds
const VOLUME_TRILHA = 0.6;    // 0.3 when there is narration on top

const [W, H] = FORMATO === 'em-pe' ? [1080, 1920] : [1920, 1080];
const out = (f, s) => writeFileSync(new URL(f, import.meta.url), s);

// [id, start, duration, z] — cuts on the 120 BPM beat grid of the soundtrack (drop at 3.0 s, one beat = 0.5 s).
// Each scene overlaps the next by ~0.15 s so its exit animation hides under the next entrance.
const slots = [
  ['fundo', 0, DUR, 0],
  ['s1-titulo', 0, 3.15, 10],
  ['s2-numeros', 3.0, 4.15, 11],
  ['s3-final', 7.0, 3.0, 12],
  ['transicoes', 0, DUR, 40],
];

// [file in assets/sfx, start, volume] — short effects between 0.2 and 0.5
const sfx = [
  ['key-press', 0.45, 0.35], ['key-press', 0.75, 0.35],
  ['whoosh', 2.76, 0.5], ['impact-bass-1', 3.0, 0.55],
  ['pop', 3.45, 0.3], ['pop', 3.8, 0.3], ['pop', 4.15, 0.3],
  ['whoosh-short', 6.82, 0.45], ['impact-bass-1', 7.0, 0.5],
  ['sparkle', 7.9, 0.35],
];
const SFX_LEN = { 'key-press': 0.4, whoosh: 0.57, 'whoosh-short': 0.57, 'whoosh-cinematic': 5.54, 'impact-bass-1': 2.12,
  'impact-bass-2': 2.59, pop: 0.72, click: 0.37, 'click-soft': 0.37, sparkle: 1.8, chime: 2.5, ping: 1.32,
  notification: 2.46, riser: 10.03, typing: 1.5, error: 1.62, 'glitch-1': 2.64, 'glitch-2': 3.5, 'glitch-3': 3.1 };

// keep every scene file's canvas size in sync with FORMATO
for (const f of readdirSync(new URL('./compositions/', import.meta.url))) {
  if (!/^s.*\.html$/.test(f)) continue;
  const p = new URL(`./compositions/${f}`, import.meta.url);
  writeFileSync(p, readFileSync(p, 'utf8').replace(/data-width="\d+" data-height="\d+"/g, `data-width="${W}" data-height="${H}"`));
}

// give every effect a lane where it never overlaps another sound
const laneEnds = [];
const sfxTags = sfx.map(([f, t, v], i) => {
  const d = Math.min(SFX_LEN[f] ?? 1, DUR - t);
  let lane = laneEnds.findIndex((end) => end <= t + 1e-6);
  if (lane < 0) { lane = laneEnds.length; laneEnds.push(0); }
  laneEnds[lane] = t + d;
  return `
    <audio id="sfx-${String(i).padStart(2, '0')}-${f}" src="assets/sfx/${f}.mp3" data-start="${t}" data-duration="${d.toFixed(2)}" data-track-index="${20 + lane}" data-volume="${v}"></audio>`;
}).join('');

const hosts = slots.map(([id, start, dur, z], i) => `
      <div id="${id}" data-composition-id="${id}" data-composition-src="compositions/${id}.html"
        data-start="${start}" data-duration="${dur}" data-track-index="${i}"
        data-width="${W}" data-height="${H}" style="z-index:${z}"></div>`).join('');

out('./index.html', `<!doctype html>
<html lang="pt-BR" data-resolution="${FORMATO === 'em-pe' ? 'portrait' : 'landscape'}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${W}, height=${H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: Poppins; font-weight: 800; src: url(assets/Poppins-ExtraBold.ttf); }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: ${W}px; height: ${H}px; overflow: hidden; background: #121212; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #121212; font-family: Poppins, sans-serif; --destaque: ${DESTAQUE}; }
      #root > div { position: absolute; inset: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${DUR}" data-width="${W}" data-height="${H}">${hosts}
    </div>

    <audio id="trilha" src="assets/trilha.wav" data-start="0" data-duration="${DUR}" data-track-index="19" data-volume="${VOLUME_TRILHA}"></audio>${sfxTags}

    <script>
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
`);

out('./compositions/fundo.html', `<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
        #root { position: absolute; inset: 0; overflow: hidden; background: #121212; }
        .fundo-glow { position: absolute; border-radius: 50%; width: 1500px; height: 1500px; }
        #fundo-glow-a { left: -700px; top: -800px; background: radial-gradient(circle, color-mix(in srgb, var(--destaque) 22%, transparent) 0%, transparent 65%); }
        #fundo-glow-b { right: -700px; bottom: -800px; background: radial-gradient(circle, rgba(120, 150, 190, 0.1) 0%, transparent 65%); }
        #fundo-grid { position: absolute; inset: -80px;
          background-image: linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
          background-size: 80px 80px;
          -webkit-mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 20%, transparent 80%);
          mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 20%, transparent 80%); }
        #fundo-vignette { position: absolute; inset: 0; background: radial-gradient(ellipse 85% 80% at 50% 50%, transparent 55%, rgba(0, 0, 0, 0.55) 100%); }
      </style>
      <div id="root" data-composition-id="fundo" data-width="${W}" data-height="${H}">
        <div id="fundo-grid"></div>
        <div id="fundo-glow-a" class="fundo-glow" data-layout-ignore></div>
        <div id="fundo-glow-b" class="fundo-glow" data-layout-ignore></div>
        <div id="fundo-vignette"></div>
      </div>
      <script>
        (function () {
          // slow drift so the frame never sits dead still
          const tl = gsap.timeline({ paused: true });
          tl.fromTo("#fundo-glow-a", { x: 0, y: 0 }, { x: 260, y: 140, duration: ${DUR}, ease: "sine.inOut" }, 0);
          tl.fromTo("#fundo-glow-b", { x: 0, y: 0 }, { x: -320, y: -160, duration: ${DUR}, ease: "sine.inOut" }, 0);
          tl.fromTo("#fundo-grid", { x: 0, y: 0 }, { x: -80, y: -40, duration: ${DUR}, ease: "none" }, 0);
          window.__timelines["fundo"] = tl;
        })();
      </script>
    </template>
  </body>
</html>
`);

// skewed wipe geometry: covers the whole frame at the cut, whatever the format
const barH = H + 600, half = Math.round((barH * Math.tan((16 * Math.PI) / 180)) / 2);
const mainW = W + 2 * half + 200;
const cover = Math.round((W - mainW) / 2), start = -mainW - half - 100, end = W + half + 100;
const WIPE = 3.0; // the cut the wipe lands on (the soundtrack drop)
const FLASHES = [7.0];

out('./compositions/transicoes.html', `<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
        #root { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
        .tr-bar { position: absolute; top: -300px; height: ${barH}px; left: 0; }
        #tr-main { width: ${mainW}px; background: var(--destaque); }
        #tr-trail { width: 140px; background: #1e1e1e; }
        #tr-lead { width: 60px; background: color-mix(in srgb, var(--destaque) 60%, white); }
        #tr-flash { position: absolute; inset: 0; background: #fffdf4; opacity: 0; }
        #tr-fade { position: absolute; inset: 0; background: #000; opacity: 0; }
      </style>
      <div id="root" data-composition-id="transicoes" data-width="${W}" data-height="${H}">
        <div id="tr-trail" class="tr-bar" data-layout-ignore></div>
        <div id="tr-main" class="tr-bar" data-layout-ignore></div>
        <div id="tr-lead" class="tr-bar" data-layout-ignore></div>
        <div id="tr-flash"></div>
        <div id="tr-fade"></div>
      </div>
      <script>
        (function () {
          const tl = gsap.timeline({ paused: true });
          // the panel covers the frame exactly on the cut, then clears to the next scene
          tl.set([".tr-bar"], { skewX: -16 }, 0);
          tl.fromTo("#tr-trail", { x: ${start - 200} }, { x: ${cover - 160}, duration: 0.3, ease: "power2.in" }, ${WIPE - 0.32});
          tl.fromTo("#tr-main", { x: ${start} }, { x: ${cover}, duration: 0.3, ease: "power2.in" }, ${WIPE - 0.3});
          tl.fromTo("#tr-lead", { x: ${-half - 200} }, { x: ${end}, duration: 0.3, ease: "power2.in" }, ${WIPE - 0.3});
          tl.to("#tr-main", { x: ${end}, duration: 0.32, ease: "power3.in" }, ${WIPE + 0.04});
          tl.to("#tr-trail", { x: ${end + 100}, duration: 0.34, ease: "power3.in" }, ${WIPE + 0.07});

          // soft light flashes on the hard cuts
          for (const t of ${JSON.stringify(FLASHES)}) {
            tl.fromTo("#tr-flash", { opacity: 0 }, { opacity: 0.16, duration: 0.05, ease: "none", immediateRender: false }, t - 0.04);
            tl.to("#tr-flash", { opacity: 0, duration: 0.3, ease: "power2.out" }, t + 0.02);
          }

          // end: fade to black under the music fade
          tl.fromTo("#tr-fade", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power1.in", immediateRender: false }, ${DUR - 0.5});
          window.__timelines["transicoes"] = tl;
        })();
      </script>
    </template>
  </body>
</html>
`);
console.log(`index.html: ${FORMATO} ${W}x${H}, ${DUR}s, ${slots.length} camadas, ${sfx.length} efeitos em ${laneEnds.length} faixas`);
