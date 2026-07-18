#!/usr/bin/env python3
"""
=========================================================
 Audio Library Toolkit
---------------------------------------------------------
 Tool       : Silence Scanner
 Version    : 0.1.0
 Author     : Raymond Ummels
 License    : MIT

 Repository :
 https://github.com/mixnetwork1959/RadioAlbenaToolkit
=========================================================

Scans MP3, FLAC, WAV, M4A, AAC and OGG files for silence
at the beginning and end.
"""

import csv
import json
import os
import re
import subprocess
import time

VERSION = "0.1.0"

FFMPEG = r"C:\ffmpeg\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffprobe.exe"

EXTENSIONS = (".mp3",".flac",".wav",".aac",".m4a",".ogg")
SILENCE_DB = -40
MIN_SILENCE = 2.0

CSV_FILE = "silence_report.csv"


def audio_files(folder):
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(EXTENSIONS):
                yield os.path.join(root, f)


def duration(file):
    cmd=[FFPROBE,"-v","quiet","-print_format","json","-show_format",file]
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return float(json.loads(p.stdout.decode("utf-8","replace"))["format"]["duration"])
    except Exception:
        return 0.0


def detect(file):
    dur=duration(file)

    cmd=[
        FFMPEG,
        "-nostdin",
        "-hide_banner",
        "-i",file,
        "-af",f"silencedetect=noise={SILENCE_DB}dB:d={MIN_SILENCE}",
        "-f","null","-"
    ]

    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    log=p.stderr.decode("utf-8","replace")

    starts=[float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)",log)]
    ends=[float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)",log)]

    intro=0.0
    outro=0.0

    if starts and ends and abs(starts[0])<0.01:
        intro=ends[0]

    if starts:
        last=starts[-1]
        if dur>=last:
            outro=dur-last

    return round(dur,2),round(intro,2),round(outro,2)


def main():

    folder=input("Musikordner: ").strip('"')

    files=list(audio_files(folder))

    total=len(files)

    if total==0:
        print("Keine Audiodateien gefunden.")
        return

    print(f"\n{total} Dateien gefunden.\n")

    start=time.time()

    rows=[]

    with open(CSV_FILE,"w",newline="",encoding="utf-8-sig") as fp:

        writer=csv.writer(fp,delimiter=";")
        writer.writerow(["Datei","Dauer","Intro","Outro"])

        for i,file in enumerate(files,1):

            try:
                dur,intro,outro=detect(file)

                row=[file,dur,intro,outro]
                rows.append(row)
                writer.writerow(row)
                fp.flush()

            except Exception as ex:
                print("FEHLER:",os.path.basename(file),ex)
                continue

            elapsed=time.time()-start
            avg=elapsed/i
            eta=(total-i)*avg

            print(
                f"[{i:5}/{total}] "
                f"{(i/total)*100:5.1f}% "
                f"ETA {time.strftime('%H:%M:%S',time.gmtime(eta))} "
                f"{os.path.basename(file)}"
            )

    rows.sort(key=lambda r:r[3],reverse=True)

    with open(CSV_FILE,"w",newline="",encoding="utf-8-sig") as fp:
        w=csv.writer(fp,delimiter=";")
        w.writerow(["Datei","Dauer","Intro","Outro"])
        w.writerows(rows)

    print("\nTop 20 längste Outros:\n")
    for r in rows[:20]:
        print(f"{r[3]:6.2f}s  {os.path.basename(r[0])}")

    print(f"\nFertig. CSV: {CSV_FILE}")


if __name__=="__main__":
    main()
