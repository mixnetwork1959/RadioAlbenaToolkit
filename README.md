#  Audio Library Toolkit

Scans MP3, FLAC, WAV, M4A, AAC and OGG files for silence at the beginning and end.

Audio Library Toolkit is a collection of Python tools for managing, analyzing and optimizing large audio libraries.

The first included tool is the Silence Scanner, which detects silence at the beginning and end of audio files.

## Current Tool

### Silence Scanner

Detects silence at the beginning and end of audio files and generates a CSV report.

## Requirements

- Windows 10 / 11
- Python 3.11+
- FFmpeg 7.x or newer

## Features

- Scan complete music library
- Detect intro silence
- Detect outro silence
- CSV report
- Fast FFmpeg based detection
- Works recursively

## Requirements

- Windows 10 / 11
- Python 3.11 or newer
- FFmpeg

## Install Python

https://www.python.org/downloads/

During installation enable

✔ Add Python to PATH

## Install FFmpeg

Download

https://www.gyan.dev/ffmpeg/builds/

Extract to

C:\ffmpeg

Folder should contain

C:\ffmpeg\
    ffmpeg.exe
    ffprobe.exe

## Run

Open CMD

```
python RadioAlbenaSilenceScanner.py
```

Choose your music folder

Example

```
D:\Music
```

The report will be written to

```
silence_report.csv
```

## 🚀 Roadmap

### Version 0.1.0
- [x] Scan music folders
- [x] Detect intro silence
- [x] Detect outro silence
- [x] CSV export

### Version 0.2.0
- [ ] Multi-core scanning
- [ ] ETA (remaining time)
- [ ] Continuous CSV writing
- [ ] Better error handling

### Version 0.3.0
- [ ] Resume interrupted scan
- [ ] Sort by intro/outro
- [ ] Detect silence start position
- [ ] Scan statistics

### Version 0.4.0
- [ ] Automatic intro trimming
- [ ] Automatic outro trimming
- [ ] Preserve folder structure
- [ ] Dry-run mode

### Planned Features
- [ ] HTML report
- [ ] BPM detection
- [ ] ReplayGain analysis
- [ ] Loudness analysis
- [ ] Cover artwork detection
- [ ] Duplicate finder


# Changelog

## 0.1.0

- Initial release
- Silence detection
- CSV export

## Planned Tools

- Duplicate Finder
- Audio Trimmer
- ReplayGain Analyzer
- BPM Scanner
- Playlist Analyzer
- Tag Normalizer


---

## Support the Project

The Audio Library Toolkit is free and open source.

If this project saves you time and you would like to support future development, you can make a voluntary donation.

❤️ PayPal: https://paypal.me/RaymundusUmmels
