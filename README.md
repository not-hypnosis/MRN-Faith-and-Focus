# MRN Focus V1.0.0

MRN Focus is a lightweight desktop timer for focused work and restorative breaks. It runs locally and keeps no account or network connection.

## Features

- Focus (25 minutes by default), Short Break (5 minutes), and Long Break (15 minutes)
- Configurable Focus sessions from 1 to 180 minutes
- Start, pause, resume, reset, and keyboard shortcuts (Space and R)
- Animated session progress and a completed Focus-session counter
- Offline motivational messages, rotated during Focus sessions
- In-app completion notification

## Technology

Python 3 with Tkinter/ttk and the Python standard library. The standalone Windows executable is packaged with PyInstaller.

## Run from Python

Install Python 3 with Tkinter, then run from this directory:

```powershell
python focus_mrn.py
```

Keep `mrn_focus.ico` beside the script.

## Standalone Windows app

Run `dist\MRN Focus.exe`. The executable is a single-file, windowed build and includes its application icon.
