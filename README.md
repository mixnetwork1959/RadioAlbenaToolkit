# Audio Library Toolkit – Silence Scanner

Tested on a real-world music library containing 12,950 audio files.

Ultra-fast intro and outro silence detection for large audio libraries.

Originally developed for **Radio Albena**, this tool scans thousands of audio files and identifies songs with long intros or outros before they are imported into radio automation software.

---

## Features

- Ultra-fast intro and outro scanning
- Multi-threaded processing
- Detects only problematic files
- Generates a CSV report
- Original audio files are never modified
- Supports:
  - MP3
  - FLAC
  - WAV
  - AAC
  - M4A
  - OGG

---

## Why?

Many music libraries contain tracks with:

- Long intros
- Long fade-outs
- Excessive silence at the beginning or end

These tracks are often unsuitable for professional radio automation.

Silence Scanner automatically detects them, allowing you to review only the files that require attention.

---

## Requirements

- Windows
- Python 3.10 or newer
- FFmpeg

---

## Usage

Run the scanner:

```bash
py silence_scanner.py
```

Enter your music folder when prompted.

After the scan, a file named **silence_report.csv** will be created.

---

## Example Output

```
Files scanned : 6191
Long Intro    : 0
Bad Outro     : 4
Errors         : 0
Elapsed        : 00:30:52
```

---

## CSV Output

Only files that require attention are written to the report.

Example:

```text
File;Intro;Outro;Problem
Song.mp3;16.25;2.09;LONG INTRO
```

---

## Workflow

1. Scan your music library.
2. Review **silence_report.csv**.
3. Run **Auto Cutter** (optional).
4. Processed files are written to the **Music_Cut** folder.
5. Original files remain untouched.

---

## Philosophy

The Audio Library Toolkit follows one simple principle:

> **Do one thing. Do it well.**

The Silence Scanner analyzes your library and reports potential issues only.

It never edits or modifies your original audio files.

---

## Roadmap

Current tools:

- ✅ Silence Scanner
- ✅ Auto Cutter

Planned:

- Audio Normalizer
- Duplicate Finder
- Metadata Checker
- Library Health Analyzer

---

## License

MIT License

---

## Author

**Raymond Ummels**

Radio Albena

https://radio-albena.com