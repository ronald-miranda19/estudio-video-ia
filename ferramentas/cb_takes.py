# Several Chatterbox takes per line (different seeds), so the best one can be picked.
#   cb_takes.py OUT_DIR TAKES EXAGGERATION CFG TSV [ONLY_IDS_COMMA]
import sys, os, time
import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

out_dir, takes, exa, cfg, tsv = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
only = set(sys.argv[6].split(",")) if len(sys.argv) > 6 else None
os.makedirs(out_dir, exist_ok=True)
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for line in open(tsv, encoding="utf-8"):
    key, text = line.rstrip("\n").split("\t", 1)
    if only and key not in only:
        continue
    for k in range(takes):
        torch.manual_seed(1000 + k)
        t0 = time.time()
        wav = model.generate(text, language_id="pt", exaggeration=exa, cfg_weight=cfg)
        ta.save(os.path.join(out_dir, f"{key}-t{k}.wav"), wav, model.sr)
        print(key, k, f"{wav.shape[-1] / model.sr:.2f}s in {time.time() - t0:.0f}s", flush=True)
