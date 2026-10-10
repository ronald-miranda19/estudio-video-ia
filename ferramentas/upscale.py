# Upscale every PNG in IN_DIR x4 with a Real-ESRGAN model (via spandrel); skips frames already done.
#   upscale.py MODEL.pth IN_DIR OUT_DIR
import sys, os, glob, time, torch, numpy as np
from PIL import Image
from spandrel import ModelLoader
dev = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
torch.set_num_threads(os.cpu_count())
model = ModelLoader().load_from_file(sys.argv[1]).eval().to(dev)
src, out = sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(os.path.join(src, '*.png')))
t0 = time.time(); done = 0
for n, f in enumerate(files):
    dst = os.path.join(out, os.path.basename(f))
    if os.path.exists(dst): continue
    x = torch.from_numpy(np.asarray(Image.open(f).convert('RGB'), dtype=np.float32) / 255).permute(2, 0, 1)[None].to(dev)
    with torch.inference_mode():
        y = model(x).clamp(0, 1)[0].permute(1, 2, 0).float().cpu().numpy()
    Image.fromarray((y * 255 + 0.5).astype(np.uint8)).save(dst, compress_level=1)
    done += 1
    if done % 25 == 1: print(f'{n + 1}/{len(files)} {(time.time() - t0) / done:.2f}s/frame on {dev}', flush=True)
print('done', done, f'{time.time() - t0:.0f}s on {dev}')
