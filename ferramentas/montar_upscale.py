# Rebuild the whole clip at W x H: AI-upscaled frame where one exists, plain Lanczos elsewhere,
# so every timestamp of the original still points at the same moment.
#   montar_upscale.py ALL_DIR UP_DIR OUT.mp4 W H FPS
import os, subprocess, sys
from PIL import Image
all_dir, up_dir, out, W, H, fps = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ff = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', fps, '-i', '-',
                       '-vf', 'unsharp=3:3:0.25', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-g', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
n = up = 0
for f in sorted(os.listdir(all_dir)):
    p = os.path.join(up_dir, f)
    if os.path.exists(p):
        im = Image.open(p).resize((W, H), Image.LANCZOS); up += 1
    else:
        im = Image.open(os.path.join(all_dir, f)).resize((W, H), Image.LANCZOS)
    ff.stdin.write(im.convert('RGB').tobytes()); n += 1
ff.stdin.close(); ff.wait(); print('frames', n, 'upscaled', up)
