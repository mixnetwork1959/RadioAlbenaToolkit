#!/usr/bin/env python3
"""
=========================================================
 Audio Library Toolkit
---------------------------------------------------------
 Tool      : Silence Scanner
 Version   : 1.0.0
 Author    : Raymond Ummels
 License   : MIT
=========================================================

Ultra Fast Silence Scanner

Detects excessive silence at the beginning and end of audio files.

Optimized for Radio Libraries
"""

import csv
import os
import re
import subprocess
import shutil
import sys
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================================================
# VERSION
# =========================================================

VERSION = "1.0.0"

# =========================================================
# SETTINGS
# =========================================================

FFMPEG = r"C:\ffmpeg\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffprobe.exe"

CSV_FILE = "silence_report.csv"

CORRUPT_FOLDER = "Corrupt_Files"

EXTENSIONS = (
    ".mp3",
    ".flac",
    ".wav",
    ".aac",
    ".m4a",
    ".ogg"
)

# ---------------------------------------------------------
# Scan

INTRO_SCAN = 20
OUTRO_SCAN = 60

MAX_INTRO = 5.0
MAX_OUTRO = 5.0

SILENCE_DB = -40
MIN_SILENCE = 2.0

OUTRO_TOLERANCE = 0.5

# ---------------------------------------------------------
# Performance

WORKERS = None

# =========================================================
# Statistics
# =========================================================

stats = {

    "files":0,

    "errors":0,

    "corrupt":0,

    "long_intro":0,

    "bad_outro":0,

    "both":0,

    "intro_total":0.0,

    "outro_total":0.0,

    "intro_found":0,

    "outro_found":0

}

# =========================================================
# Helpers
# =========================================================

def format_time(seconds):

    return time.strftime(
        "%H:%M:%S",
        time.gmtime(seconds)
    )


def check_ffmpeg():

    if not os.path.isfile(FFMPEG):

        print()

        print("FFmpeg not found")

        print(FFMPEG)

        sys.exit(1)


def audio_files(folder):

    for root, _, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(EXTENSIONS):

                yield os.path.join(root,file)



def ensure_corrupt_folder():
    os.makedirs(CORRUPT_FOLDER, exist_ok=True)

def move_corrupt_file(filename):
    ensure_corrupt_folder()
    base = os.path.basename(filename)
    dest = os.path.join(CORRUPT_FOLDER, base)
    name, ext = os.path.splitext(base)
    i = 1
    while os.path.exists(dest):
        dest = os.path.join(CORRUPT_FOLDER, f"{name}_{i}{ext}")
        i += 1
    try:
        shutil.move(filename, dest)
        stats["corrupt"] += 1
        return dest
    except Exception:
        return None

# =========================================================
# FFmpeg
# =========================================================

def run_ffmpeg(cmd):

    result = subprocess.run(

        cmd,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",

        errors="replace"

    )

    return result.returncode, result.stderr


# =========================================================
# Silence Parser
# =========================================================

def parse_silence(log):

    blocks=[]

    start=None

    for line in log.splitlines():

        if "silence_start:" in line:

            try:

                start=float(

                    line.split(

                        "silence_start:"

                    )[1].strip()

                )

            except:

                start=None

        elif "silence_end:" in line and start is not None:

            try:

                end=float(

                    line.split(

                        "silence_end:"

                    )[1].split("|")[0].strip()

                )

                blocks.append(

                    (start,end)

                )

                start=None

            except:

                pass

    return blocks
    # =========================================================
# Scan one file
# =========================================================

def scan_file(filename):

    intro = 0.0
    outro = 0.0
    status = "OK"

    #
    # ---------- INTRO ----------
    #

    cmd = [

        FFMPEG,

        "-hide_banner",

        "-nostats",

        "-t",
        str(INTRO_SCAN),

        "-i",
        filename,

        "-af",
        f"silencedetect=noise={SILENCE_DB}dB:d={MIN_SILENCE}",

        "-f",
        "null",

        "-"
    ]

    rc, log = run_ffmpeg(cmd)
    if rc != 0 or "Invalid data" in log:
        move_corrupt_file(filename)
        return (filename,0.0,0.0,"ERROR")

    blocks = parse_silence(log)

    if blocks:

        start, end = blocks[0]

        if start <= 0.05:

            intro = round(end,2)

    #
    # ---------- OUTRO ----------
    # v0.4.0: extended analysis window (60 s) and FFprobe support prepared.
    #

    cmd = [

        FFMPEG,

        "-hide_banner",

        "-nostats",

        "-sseof",
        f"-{OUTRO_SCAN}",

        "-i",
        filename,

        "-t",
        str(OUTRO_SCAN),

        "-af",
        f"silencedetect=noise={SILENCE_DB}dB:d={MIN_SILENCE}",

        "-f",
        "null",

        "-"
    ]

    rc, log = run_ffmpeg(cmd)
    if rc != 0 or "Invalid data" in log:
        move_corrupt_file(filename)
        return (filename,0.0,0.0,"ERROR")

    blocks = parse_silence(log)

    if blocks:

        start, end = blocks[-1]

        #
        # Letzter Silenceblock endet am Scanende
        #

        if abs(end - OUTRO_SCAN) <= OUTRO_TOLERANCE:

            outro = round(
                OUTRO_SCAN - start,
                2
            )

    #
    # ---------- Status ----------
    #

    if intro > MAX_INTRO:

        status = "LONG INTRO"

    if outro > MAX_OUTRO:

        if status == "LONG INTRO":

            status = "LONG INTRO + BAD OUTRO"

        else:

            status = "BAD OUTRO"

    return (

        filename,

        intro,

        outro,

        status

    )
    # =========================================================
# Statistics
# =========================================================

def update_stats(result):

    _, intro, outro, status = result

    stats["files"] += 1

    if status == "ERROR":

        stats["errors"] += 1
        return

    if intro > 0:

        stats["intro_found"] += 1
        stats["intro_total"] += intro

    if outro > 0:

        stats["outro_found"] += 1
        stats["outro_total"] += outro

    if status == "LONG INTRO":

        stats["long_intro"] += 1

    elif status == "BAD OUTRO":

        stats["bad_outro"] += 1

    elif status == "LONG INTRO + BAD OUTRO":

        stats["both"] += 1


# =========================================================
# Scan Library
# =========================================================

def scan_library(files):

    rows = []

    total = len(files)

    start = time.time()

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        futures = {

            executor.submit(
                scan_file,
                filename
            ): filename

            for filename in files

        }

        for index, future in enumerate(
            as_completed(futures),
            start=1
        ):

            try:

                result = future.result()

            except Exception:

                stats["files"] += 1
                stats["errors"] += 1
                continue

            update_stats(result)

            if result[3] != "OK":

                rows.append(result)

            elapsed = time.time() - start

            eta = (
                elapsed / index
            ) * (
                total - index
            )

            print(

                f"\r"

                f"[{index:5}/{total}] "

                f"{index/total*100:5.1f}% "

                f"ETA {format_time(eta)}",

                end="",

                flush=True

            )

    print()

    return rows


# =========================================================
# CSV
# =========================================================

def save_csv(rows):

    priority = {

        "LONG INTRO + BAD OUTRO": 0,

        "LONG INTRO": 1,

        "BAD OUTRO": 2,

        "ERROR": 3

    }

    rows.sort(

        key=lambda row: (

            priority.get(row[3],99),

            row[0].lower()

        )

    )

    with open(

        CSV_FILE,

        "w",

        newline="",

        encoding="utf-8-sig"

    ) as fp:

        writer = csv.writer(

            fp,

            delimiter=";"

        )

        writer.writerow([

            "File",

            "Intro",

            "Outro",

            "Problem"

        ])

        writer.writerows(rows)
        # =========================================================
# Summary
# =========================================================

def print_summary(elapsed):

    print()
    print("=" * 60)
    print("Audio Library Toolkit")
    print(f"Silence Scanner {VERSION}")
    print("=" * 60)

    print(f"Files scanned : {stats['files']}")
    print(f"Long Intro    : {stats['long_intro']}")
    print(f"Bad Outro     : {stats['bad_outro']}")
    print(f"Both          : {stats['both']}")
    print(f"Corrupt Files : {stats['corrupt']}")
    print(f"Errors        : {stats['errors']}")

    print("-" * 60)

    problems = (
        stats["long_intro"] +
        stats["bad_outro"] +
        stats["both"]
    )

    print(f"Problem files : {problems}")

    if stats["intro_found"]:

        avg_intro = (
            stats["intro_total"] /
            stats["intro_found"]
        )

        print(f"Average Intro : {avg_intro:.2f} sec")

    if stats["outro_found"]:

        avg_outro = (
            stats["outro_total"] /
            stats["outro_found"]
        )

        print(f"Average Outro : {avg_outro:.2f} sec")

    print(f"CSV           : {CSV_FILE}")

    print(
        f"Elapsed       : "
        f"{format_time(elapsed)}"
    )


# =========================================================
# Main
# =========================================================

def main():

    check_ffmpeg()

    folder = input(
        "Music folder: "
    ).strip('"')

    if not os.path.isdir(folder):

        print()

        print("Folder not found.")

        return

    files = list(
        audio_files(folder)
    )

    if not files:

        print()

        print("No audio files found.")

        return

    print()

    print(
        f"Found {len(files)} audio files."
    )

    print()

    start = time.time()

    rows = scan_library(files)

    save_csv(rows)

    elapsed = (
        time.time() - start
    )

    print_summary(elapsed)
    # =========================================================
# Program Start
# =========================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()

        print("Scan cancelled by user.")