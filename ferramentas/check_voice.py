# Read a whole file aloud back as text, to check TTS pronunciation.  check_voice.py A.wav [B.wav ...]
import sys
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    segs, info = m.transcribe(f, language="pt", word_timestamps=False)
    print(f, "|", " ".join(s.text.strip() for s in segs))
