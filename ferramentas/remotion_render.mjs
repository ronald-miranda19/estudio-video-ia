// Render a Remotion composition on this PC, where Windows Smart App Control blocks Remotion's own encoder:
// Remotion exports PNG frames through the installed Google Chrome, then the system FFmpeg joins them.
// The frames come out silent: pass an audio file (e.g. the final mix) to put it under the video.
//   node ferramentas/remotion_render.mjs COMPOSITION OUT.mp4 [FPS=30] [AUDIO]
import { execSync } from 'node:child_process';
import { mkdtempSync, rmSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const [comp, outArg, fps = '30', audio] = process.argv.slice(2);
if (!comp || !outArg) { console.error('uso: node ferramentas/remotion_render.mjs COMPOSITION OUT.mp4 [FPS] [AUDIO]'); process.exit(1); }
const out = resolve(outArg);
const chrome = process.env.HYPERFRAMES_BROWSER_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const remotionDir = resolve(import.meta.dirname, '..', 'remotion');
const frames = mkdtempSync(join(tmpdir(), 'remotion-quadros-'));
const run = (cmd, cwd) => execSync(cmd, { cwd, stdio: 'inherit', shell: true });

run(`npx remotion render ${comp} "${frames}" --sequence --image-format=png --browser-executable="${chrome}" --chrome-mode=chrome-for-testing`, remotionDir);
const first = readdirSync(frames).filter(f => f.endsWith('.png')).sort()[0];
const pattern = first.replace(/\d+\.png$/, m => `%0${m.length - 4}d.png`);
const audioIn = audio ? `-i "${resolve(audio)}" -map 0:v -map 1:a -c:a aac -b:a 192k -shortest` : '';
run(`ffmpeg -nostdin -y -loglevel error -framerate ${fps} -i "${join(frames, pattern)}" ${audioIn} -c:v libx264 -crf 16 -pix_fmt yuv420p -movflags +faststart "${out}"`);
rmSync(frames, { recursive: true, force: true });
console.log('pronto:', out);
