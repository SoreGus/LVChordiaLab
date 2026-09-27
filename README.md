# LVChordiaLab

LVChordiaLab is a macOS desktop application for evaluating chord recognition with [lv-chordia](https://github.com/openmirlab/lv-chordia).

The application provides a graphical interface for loading audio files, running chord recognition locally, and reviewing the detected progression on a synchronized timeline.

## Requirements

- macOS
- Apple Silicon
- Python 3.12
- FFmpeg
- Homebrew

Linux is not currently supported by this project and may require adaptations to the environment, audio stack, and dependency setup.

## Installation

Install Python 3.12:

```bash
brew install python@3.12
```

Install FFmpeg:

```bash
brew install ffmpeg
```

Verify the installations:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 --version
ffmpeg -version
```

## Configuration

Create the local environment file:

```bash
cp .env.example .env
```

Recommended configuration:

```env
PYTHON_BIN=/opt/homebrew/opt/python@3.12/bin/python3.12

LV_CHORDIA_DEVICE=auto
LV_CHORDIA_CHORD_DICT=full
LV_CHORDIA_LOG_LEVEL=INFO
```

### Chord Dictionary

`LV_CHORDIA_CHORD_DICT` defines the chord vocabulary used by lv-chordia.

Available options include:

- `ismir2017`
- `submission`
- `full`

The project currently uses:

```env
LV_CHORDIA_CHORD_DICT=full
```

## Setup

From the project root, create the virtual environment and install all dependencies:

```bash
make setup
```

## Running

Start the application with:

```bash
make run
```

## Usage

1. Launch the application.
2. Select an audio file using **Choose Audio**, or drag a file into the window.
3. Wait for chord recognition to complete.
4. Review the detected chords on the timeline.
5. Play the audio to follow the progression in sync.
6. Click a chord segment to seek directly to that position.
7. Scroll or zoom the timeline when working with longer recordings.

Analysis results remain in memory and are displayed only in the application.

## Features

- Local chord recognition
- Audio file picker
- Drag and drop
- Synchronized audio playback
- Visual chord timeline
- Current chord tracking
- Seek by chord segment
- Horizontal scrolling
- Timeline zoom
- Background analysis without blocking the interface

## Development

Install or update dependencies:

```bash
make install
```

Run the application:

```bash
make run
```

Run lint checks:

```bash
make lint
```

Format the source code:

```bash
make format
```

Run project checks:

```bash
make check
```

Remove the virtual environment and generated caches:

```bash
make clean
```

## Current Scope

LVChordiaLab currently performs chord recognition from complete audio files.

Real-time microphone recognition is not implemented at this stage.

The project is intended to evaluate the practical quality of lv-chordia before further work on streaming recognition, alternative models, or Apple-native deployment.

## Reference

lv-chordia  
Open MIR Lab

https://github.com/openmirlab/lv-chordia