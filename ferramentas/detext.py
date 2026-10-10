# Remove a caption that stays fixed on screen while the footage changes underneath.
# Pixels that keep the same colour through every scene inside the caption band are the text
# (white fill + dark outline + emoji); each frame is then inpainted under that mask.
#   detext.py FRAMES_DIR OUT_DIR MASK_PNG Y0 Y1
import sys, os, glob
import numpy as np
import cv2

src, out, mask_path, y0, y1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(os.path.join(src, "*.png")))
stack = np.stack([cv2.imread(f) for f in files]).astype(np.float32)  # T,H,W,3
band = stack[:, y0:y1]
std = band.std(axis=0).mean(axis=2)        # how much each pixel changes over time
mean = band.mean(axis=0)
lum = mean.mean(axis=2)
# static pixels in the band: the text. Bright fill, dark outline, or the coloured emoji.
static = std < 14
mask_band = (static & ((lum > 170) | (lum < 70))).astype(np.uint8) * 255
emoji = (static & (np.abs(mean[..., 2] - mean[..., 0]) > 40)).astype(np.uint8) * 255  # yellow/red vs blue
mask_band = cv2.bitwise_or(mask_band, emoji)
# keep only blobs that look like glyphs (drop big static background areas)
n, lab, stats, _ = cv2.connectedComponentsWithStats(mask_band, 8)
clean = np.zeros_like(mask_band)
for i in range(1, n):
    x, y, w, h, area = stats[i]
    if area >= 3 and h <= 75:
        clean[lab == i] = 255
clean = cv2.dilate(clean, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)), iterations=1)
H, W = stack.shape[1:3]
mask = np.zeros((H, W), np.uint8)
mask[y0:y1] = clean
cv2.imwrite(mask_path, mask)
print("mask pixels", int((mask > 0).sum()), "of", H * W)
for f in files:
    img = cv2.imread(f)
    fixed = cv2.inpaint(img, mask, 6, cv2.INPAINT_TELEA)
    cv2.imwrite(os.path.join(out, os.path.basename(f)), fixed)
print("frames", len(files))
