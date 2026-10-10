# Transcribe every take and keep the one closest to the script (no extra words, no swaps).
#   pick_takes.py TAKES_DIR TSV OUT_DIR
import sys, os, re, glob, shutil, difflib, unicodedata
from faster_whisper import WhisperModel

takes_dir, tsv, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)
NUM = {"1": "um", "4,6": "quatro virgula seis", "800": "oitocentos", "1500": "mil e quinhentos", "1.500": "mil e quinhentos",
       "1.800": "mil e oitocentos", "mil": "mil"}

def norm(s):
    s = s.lower()
    for k, v in sorted(NUM.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.replace("pra ", "para ").replace(" ta ", " esta ")
    return re.sub(r"[^a-z ]+", " ", s).split()

m = WhisperModel("small", device="cpu", compute_type="int8")
for line in open(tsv, encoding="utf-8"):
    key, text = line.rstrip("\n").split("\t", 1)
    want = norm(text)
    best = None
    for f in sorted(glob.glob(os.path.join(takes_dir, f"{key}-t*.wav"))):
        segs, _ = m.transcribe(f, language="pt", word_timestamps=True)
        words = [w for s in segs for w in s.words]
        got_text = " ".join(w.word.strip() for w in words)
        got = norm(got_text)
        score = difflib.SequenceMatcher(None, want, got).ratio()
        end = words[-1].end if words else 0
        if best is None or score > best[0]:
            best = (score, f, got_text, end)
    score, f, got_text, end = best
    shutil.copy(f, os.path.join(out_dir, f"{key}.wav"))
    with open(os.path.join(out_dir, f"{key}.end"), "w") as fh:
        fh.write(f"{end:.3f}")
    print(f"{key} {score:.2f} end={end:.2f}s {os.path.basename(f)} | {got_text}", flush=True)
