#!/usr/bin/env bash
# Approved "Dora melhorada" chain: trim silence, EQ, gentle compression, tiny room, -16 LUFS.
#   masterizar_voz.sh IN.wav OUT.wav
set -e
ffmpeg -nostdin -y -loglevel error -i "$1" -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,highpass=f=75,equalizer=f=170:t=q:w=0.9:g=2.2,equalizer=f=320:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.0:g=1.6,equalizer=f=7200:t=q:w=1.6:g=-3.5,equalizer=f=11000:t=q:w=1.0:g=-2,acompressor=threshold=-21dB:ratio=2.6:attack=6:release=90:makeup=2,aecho=0.85:0.5:22|37:0.10|0.06,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 "$2"
