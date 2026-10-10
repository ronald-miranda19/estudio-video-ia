# Timed transcript of an audio or video file.  ts.py FILE
import sys
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language="pt")
for s in segs: print(f"{s.start:6.1f}-{s.end:6.1f} {s.text.strip()}")
