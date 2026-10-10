# AI narration in one command: script (one sentence per line) -> Kokoro voice -> mastering -> Whisper check -> narracao.wav
#   python ferramentas/narrar.py ROTEIRO.txt PASTA_SAIDA [--voz pf_dora] [--velocidade 1.04] [--pausa 0.35]
# Blank lines and lines starting with # are skipped. Writes, inside PASTA_SAIDA:
#   bruto/NN.wav (raw voice), final/NN.wav (mastered, -16 LUFS), narracao.wav (everything joined with pauses),
#   tempos.tsv (start/end of each sentence inside narracao.wav, to sync the scenes) and conferencia.tsv (what Whisper heard).
import argparse, difflib, os, re, subprocess, sys, unicodedata, urllib.request
from pathlib import Path

import soundfile as sf

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
# Same chain as ferramentas/masterizar_voz.sh: trim silence, EQ, gentle compression, tiny room, -16 LUFS.
MASTER = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "highpass=f=75,equalizer=f=170:t=q:w=0.9:g=2.2,equalizer=f=320:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.0:g=1.6,"
          "equalizer=f=7200:t=q:w=1.6:g=-3.5,equalizer=f=11000:t=q:w=1.0:g=-2,acompressor=threshold=-21dB:ratio=2.6:attack=6:release=90:makeup=2,"
          "aecho=0.85:0.5:22|37:0.10|0.06,loudnorm=I=-16:TP=-1.5:LRA=7")


def model_files():
    # reuse the copy HyperFrames already downloaded; otherwise fetch into modelos/kokoro
    hf = Path.home() / ".cache" / "hyperframes" / "tts"
    pairs = [(hf / "models" / "kokoro-v1.0.onnx", hf / "voices" / "voices-v1.0.bin")]
    local = Path(__file__).resolve().parent.parent / "modelos" / "kokoro"
    pairs.append((local / "kokoro-v1.0.onnx", local / "voices-v1.0.bin"))
    for m, v in pairs:
        if m.exists() and v.exists():
            return m, v
    local.mkdir(parents=True, exist_ok=True)
    for url, dst in [(MODEL_URL, pairs[1][0]), (VOICES_URL, pairs[1][1])]:
        print("baixando", url, flush=True)
        urllib.request.urlretrieve(url, dst)
    return pairs[1]


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("saida")
    ap.add_argument("--voz", default="pf_dora")
    ap.add_argument("--lingua", default="pt-br")
    ap.add_argument("--velocidade", type=float, default=1.04)
    ap.add_argument("--pausa", type=float, default=0.35, help="silêncio entre frases, em segundos")
    ap.add_argument("--sem-conferencia", action="store_true", help="pula a transcrição com Whisper")
    a = ap.parse_args()

    lines = [l.strip() for l in Path(a.roteiro).read_text(encoding="utf-8").splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]
    if not lines:
        sys.exit("o roteiro está vazio")
    out = Path(a.saida)
    (out / "bruto").mkdir(parents=True, exist_ok=True)
    (out / "final").mkdir(parents=True, exist_ok=True)

    from kokoro_onnx import Kokoro
    m, v = model_files()
    tts = Kokoro(str(m), str(v))
    finals = []
    for i, text in enumerate(lines, 1):
        samples, sr = tts.create(text, voice=a.voz, speed=a.velocidade, lang=a.lingua)
        raw = out / "bruto" / f"{i:02d}.wav"
        fin = out / "final" / f"{i:02d}.wav"
        sf.write(raw, samples, sr)
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(raw), "-af", MASTER, "-ar", "48000", str(fin)], check=True)
        finals.append(fin)
        print(f"{i:02d} ok  {sf.info(fin).duration:5.2f}s  {text}", flush=True)

    # join with pauses and record where each sentence lands
    sil = out / "final" / "_pausa.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                    "-t", str(a.pausa), str(sil)], check=True)
    lst = out / "final" / "_lista.txt"
    t = 0.0
    with open(lst, "w", encoding="utf-8") as fl, open(out / "tempos.tsv", "w", encoding="utf-8") as ft:
        ft.write("frase\tinicio\tfim\ttexto\n")
        for i, (fin, text) in enumerate(zip(finals, lines), 1):
            d = sf.info(fin).duration
            ft.write(f"{i:02d}\t{t:.2f}\t{t + d:.2f}\t{text}\n")
            fl.write(f"file '{fin.resolve().as_posix()}'\n")
            t += d
            if i < len(finals):
                fl.write(f"file '{sil.resolve().as_posix()}'\n")
                t += a.pausa
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "pcm_s16le", "-ar", "48000", str(out / "narracao.wav")], check=True)
    sil.unlink(); lst.unlink()
    print(f"\nnarracao.wav: {t:.2f}s  |  tempos de cada frase em tempos.tsv")

    if a.sem_conferencia:
        return
    # Kokoro sometimes swaps words: read every sentence back with Whisper and compare with the script
    from faster_whisper import WhisperModel
    w = WhisperModel("small", device="cpu", compute_type="int8")
    bad = 0
    with open(out / "conferencia.tsv", "w", encoding="utf-8") as fc:
        fc.write("frase\tnota\tescrito\touvido\n")
        for i, (fin, text) in enumerate(zip(finals, lines), 1):
            segs, _ = w.transcribe(str(fin), language=a.lingua.split("-")[0])
            heard = " ".join(s.text.strip() for s in segs)
            score = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
            flag = "" if score >= 0.85 else "  <-- REVISAR"
            bad += bool(flag)
            fc.write(f"{i:02d}\t{score:.2f}\t{text}\t{heard}\n")
            print(f"{i:02d} {score:.2f}{flag}\n   escrito: {text}\n   ouvido:  {heard}", flush=True)
    print(f"\n{bad} frase(s) para revisar. Dica: escreva siglas e nomes estrangeiros como se fala, ou troque a frase por outras palavras."
          if bad else "\ntodas as frases conferem com o roteiro.")


if __name__ == "__main__":
    main()
