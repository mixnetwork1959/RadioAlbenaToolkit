#!/usr/bin/env python3
"""
=========================================================
 Audio Library Toolkit
---------------------------------------------------------
 Tool      : Silence Scanner
 Version   : 0.2.2
 Author    : Raymond Ummels
 License   : MIT
=========================================================
"""

import csv
import json
import os
import subprocess
import sys
import time

VERSION = "0.2.2"

FFMPEG = r"C:\ffmpeg\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffprobe.exe"

CSV_FILE = "silence_report.csv"

EXTENSIONS = (".mp3",".flac",".wav",".aac",".m4a",".ogg")

SILENCE_DB = -40
MIN_SILENCE = 2.0
OUTRO_TOLERANCE = 0.5
MAX_INTRO = 15.0
MAX_OUTRO = 30.0

stats = {
    "files":0,"errors":0,
    "intro_found":0,"outro_found":0,
    "intro_total":0.0,"outro_total":0.0,
}

def audio_files(folder):
    for root,_,files in os.walk(folder):
        for f in files:
            if f.lower().endswith(EXTENSIONS):
                yield os.path.join(root,f)

def check_ffmpeg():
    if not os.path.isfile(FFMPEG):
        print("FFmpeg not found:",FFMPEG); sys.exit(1)
    if not os.path.isfile(FFPROBE):
        print("FFprobe not found:",FFPROBE); sys.exit(1)

def get_duration(fn):
    cmd=[FFPROBE,"-v","quiet","-print_format","json","-show_format",fn]
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace")
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        stats["errors"]+=1
        return 0.0

def format_time(sec):
    return time.strftime("%H:%M:%S",time.gmtime(sec))

def run_ffmpeg(fn):
    cmd=[FFMPEG,"-nostdin","-hide_banner","-i",fn,"-af",f"silencedetect=noise={SILENCE_DB}dB:d={MIN_SILENCE}","-f","null","-"]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace")
    return r.stderr

def parse_silence(log):
    blocks=[]
    start=None
    for line in log.splitlines():
        if "silence_start:" in line:
            try: start=float(line.split("silence_start:")[1].strip())
            except: start=None
        elif "silence_end:" in line and start is not None:
            try:
                end=float(line.split("silence_end:")[1].split("|")[0].strip())
                blocks.append((start,end))
                start=None
            except: pass
    return blocks

def detect_silence(fn):
    duration=get_duration(fn)
    if duration<=0:
        stats["files"]+=1
        return (0.0,0.0,0.0,"ERROR")
    intro=0.0
    outro=0.0
    status="OK"
    blocks=parse_silence(run_ffmpeg(fn))
    if blocks:
        s,e=blocks[0]
        if s<=0.05:
            intro=round(e,2)
            stats["intro_found"]+=1
            stats["intro_total"]+=intro
            if intro>MAX_INTRO:
                status="LONG INTRO"
    for s,e in reversed(blocks):
        if abs(e-duration)<=OUTRO_TOLERANCE:
            val=max(0.0,round(duration-s,2))
            if val>MAX_OUTRO:
                status="LONG INTRO + BAD OUTRO" if status=="LONG INTRO" else "BAD OUTRO"
                val=0.0
            outro=val
            if outro>0:
                stats["outro_found"]+=1
                stats["outro_total"]+=outro
            break
    stats["files"]+=1
    return (round(duration,2),round(intro,2),round(outro,2),status)

def open_csv():
    fp=open(CSV_FILE,"w",newline="",encoding="utf-8-sig")
    w=csv.writer(fp,delimiter=";")
    w.writerow(["File","Duration","Intro","Outro","Status"])
    fp.flush()
    return fp,w

def append_csv(fp,w,row):
    w.writerow(row); fp.flush()

def sort_csv(rows):
    rows.sort(key=lambda r:(r[4]=="OK",-r[3]))
    with open(CSV_FILE,"w",newline="",encoding="utf-8-sig") as fp:
        w=csv.writer(fp,delimiter=";")
        w.writerow(["File","Duration","Intro","Outro","Status"])
        w.writerows(rows)

def print_summary(elapsed):
    print("\n"+"="*55)
    print("Audio Library Toolkit")
    print(f"Silence Scanner {VERSION}")
    print("="*55)
    print(f"Files scanned : {stats['files']}")
    print(f"Errors        : {stats['errors']}")
    print(f"CSV           : {CSV_FILE}")
    print(f"Elapsed       : {format_time(elapsed)}")

def main():
    check_ffmpeg()
    folder=input("Music folder: ").strip('"')
    if not os.path.isdir(folder):
        print("Folder not found."); return
    files=list(audio_files(folder))
    fp,w=open_csv()
    rows=[]
    start=time.time()
    total=len(files)
    for index,filename in enumerate(files,start=1):
        try:
            duration,intro,outro,status=detect_silence(filename)
            row=[filename,duration,intro,outro,status]
            append_csv(fp,w,row)
            rows.append(row)
        except Exception as ex:
            stats["errors"]+=1
            print(f"\nERROR: {os.path.basename(filename)}")
            print(ex)
        elapsed=time.time()-start
        eta=(elapsed/index)*(total-index)
        print(f"\r[{index:5}/{total}] {index/total*100:5.1f}% ETA {format_time(eta)} {os.path.basename(filename):<80}",end="",flush=True)
    fp.close()
    sort_csv(rows)
    print()
    print_summary(time.time()-start)

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScan cancelled.")
