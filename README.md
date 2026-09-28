# Diskette Demolition

A tiny 16-bit-inspired Pygame game with chunky 3D voxel-style graphics.

## Platforms

- Windows 11 x64
- macOS Apple Silicon
- Python source

## Controls

| Key | Action |
|---|---|
| WASD / Arrow Keys | Move |
| Space | Smash nearby disks |
| E | Open nearest disk |
| B | Put open disk in Bin |
| U | Open Internet Archive |
| Esc | Close disk / quit |
| R | Restart after game over |

## Concept

You are surrounded by floppy disks.

Open them.

Inspect their contents.

Throw them in the Bin.

Or open the retro browser and visit the Internet Archive.

Then smash more disks.

## Build

Install Python 3.11+.

Install dependencies:

    python -m pip install -r requirements.txt

Run:

    python src/main.py

Build on macOS:

    ./build_macos.sh

Build on Windows:

    build_windows.bat

## Native Builds

PyInstaller produces native binaries.

A Windows `.exe` must be built on Windows.

A macOS `.app` must be built on macOS.

The included GitHub Actions workflow builds both automatically.

## Size

The game deliberately uses procedural graphics rather than large image
or 3D asset files. The project is intended to remain comfortably below
100 MB when packaged.
