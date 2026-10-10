# Contact sheet: the whole video in one image, one frame every N seconds with its time written on it.
# Video is checked by looking at frames, never by reading code.
#   python ferramentas/folha.py VIDEO.mp4 FOLHA.jpg [SEGUNDOS_ENTRE_QUADROS=1] [COLUNAS=10] [LARGURA_DO_QUADRO=240]
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

video, out = sys.argv[1], sys.argv[2]
step = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 10
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 240

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                           capture_output=True, text=True, check=True).stdout.strip())
tiles = []
with tempfile.TemporaryDirectory() as tmp:
    t, n = 0.0, 0
    while t < dur:
        f = os.path.join(tmp, f"{n:04d}.png")
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", video,
                        "-frames:v", "1", "-vf", f"scale={tw}:-2", f], check=True)
        if os.path.exists(f):
            im = Image.open(f).convert("RGB")
            d = ImageDraw.Draw(im)
            label = f"{int(t // 60):02d}:{t % 60:05.2f}"
            d.rectangle([0, 0, 8 + 7 * len(label), 16], fill=(0, 0, 0))
            d.text((4, 2), label, fill=(255, 220, 0))
            tiles.append(im)
        t += step
        n += 1

if not tiles:
    sys.exit("nenhum quadro extraído")
w, h = tiles[0].size
rows = (len(tiles) + cols - 1) // cols
gap = 4
sheet = Image.new("RGB", (cols * (w + gap) + gap, rows * (h + gap) + gap), (24, 24, 24))
for i, im in enumerate(tiles):
    sheet.paste(im, (gap + (i % cols) * (w + gap), gap + (i // cols) * (h + gap)))
sheet.save(out, quality=88)
print(f"{out}: {len(tiles)} quadros de {dur:.1f}s")
