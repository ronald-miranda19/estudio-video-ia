// Starts a new video from the template: copies modelo/ to projetos/<nome>, brings in fonts, GSAP and sound effects,
// generates an original soundtrack of the right length and builds index.html.
//   node ferramentas/novo-projeto.mjs <nome> [deitado|em-pe] [duracao_em_segundos=10]
import { cpSync, copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve } from 'node:path';

const [nome, formato = 'deitado', dur = '10'] = process.argv.slice(2);
if (!nome || !['deitado', 'em-pe'].includes(formato)) {
  console.error('uso: node ferramentas/novo-projeto.mjs <nome> [deitado|em-pe] [duracao_em_segundos]');
  process.exit(1);
}
const raiz = resolve(import.meta.dirname, '..');
const destino = join(raiz, 'projetos', nome);
if (existsSync(destino)) { console.error('já existe:', destino); process.exit(1); }

cpSync(join(raiz, 'modelo'), destino, { recursive: true });
const assets = join(destino, 'assets');
mkdirSync(join(assets, 'sfx'), { recursive: true });
mkdirSync(join(destino, 'renders'), { recursive: true });

// fonts, GSAP and the HyperFrames sound effects (Pixabay licence: free for commercial use)
for (const f of readdirSync(join(raiz, 'recursos', 'fontes'))) if (f.endsWith('.ttf')) copyFileSync(join(raiz, 'recursos', 'fontes', f), join(assets, f));
copyFileSync(join(raiz, 'node_modules', 'gsap', 'dist', 'gsap.min.js'), join(assets, 'gsap.min.js'));
const sfxDir = join(raiz, 'node_modules', 'hyperframes', 'dist', 'skills', 'media-use', 'audio', 'assets', 'sfx');
for (const f of readdirSync(sfxDir)) if (f.endsWith('.mp3') || f === 'CREDITS.md') copyFileSync(join(sfxDir, f), join(assets, 'sfx', f));

// format and length
const build = join(destino, 'build.mjs');
writeFileSync(build, readFileSync(build, 'utf8')
  .replace(/const FORMATO = '[^']*';/, `const FORMATO = '${formato}';`)
  .replace(/const DUR = [\d.]+;/, `const DUR = ${Number(dur)};`));

// original soundtrack: 120 BPM, drop at 3 s, fades out over the last 1.4 s
const py = [join(raiz, '.venv', 'Scripts', 'python.exe'), join(raiz, '.venv', 'bin', 'python')].find(existsSync) ?? 'python';
try {
  execFileSync(py, [join(raiz, 'ferramentas', 'music.py'), join(assets, 'trilha.wav'), String(dur), '3.0', String(Number(dur) - 1.4)], { stdio: 'inherit' });
} catch {
  console.warn('não consegui gerar a trilha (precisa da .venv com numpy e soundfile). Coloque um assets/trilha.wav antes de renderizar.');
}

execFileSync(process.execPath, [build], { stdio: 'inherit', cwd: destino });
console.log(`
pronto: ${destino}
próximos passos (dentro dessa pasta):
  npx hyperframes preview        prévia no navegador
  npx hyperframes check          confere erros, layout e contraste
  npx hyperframes render -q delivery -o renders/${nome}-bruto.mp4
Ajuste as cenas em compositions/ e a ordem, os tempos e os efeitos em build.mjs; rode "node build.mjs" após mudar o build.`);
