# Resolve Subtitle Generator

A Python script that generates SRT subtitle files from audio and video files using DaVinci Resolve's auto-captioning feature.

## Prerequisites

1. **DaVinci Resolve Studio** (version 18 or later)
2. **Python 3.6+** (64-bit version)
3. **Required Python packages** (install using `pip install -r requirements.txt`)

## Usage

1. **Start DaVinci Resolve** and create a new project or open an existing one. It won't work without Resolve running as it still uses the UI for functionality, but still fortunately in an automated way.
2. **Run the script** with one or more audio or video files as arguments:

```bash
# Process a single file
python generate_srt.py "path/to/your/audio.mp3"

# Process multiple files
python generate_srt.py "audio1.mp3" "audio2.mp3" "audio3.mp3"

# Process all M4A files in a directory
python generate_srt.py "samples/*.m4a"
```

The script will:
1. Create a timeline for each file
2. Generate subtitles using Resolve's auto-captioning
3. Export the subtitles as SRT files in the same directory as the input files

## Output

For each input file, a corresponding SRT file will be created in the same directory as the original source with the same name (but with `.srt` extension). For example:
- Input: `samples/audio1.mp3`
- Output: `samples/audio1.srt`

This holds even when using conversion flags — the SRT is always saved next to the original, not the converted temp file.

## Notes

- To minimize current random glitches that exist (see [issues](https://github.com/zinsy23/resolve-subtitle-generator/issues)), let the script itself import the media rather than yourself and have the master bin selected
- The script requires DaVinci Resolve to be running and a project to be open
- The script will create timelines in the current project
- The generated SRT files include bold formatting and proper line breaks
- The version of my script does my typical preferred settings, so you may consider modifying the `create_subtitles_from_audio()` function in generate_srt.py to match your settings.
    - I haven't tested single line SRT creation yet since it has linebreak logic in it for double lines
- I generated this program using AI until it did my desired behavior, so please excuse any brevity in this project since I'm more concerned about being able to use it as a tool for myself.

## Executing script from any directory

Here's how I recommend you execute the script from any directory:

#### **On Windows:**

1. Set an environment variable to the directory of the script:

   a. Press `Win + R` to open the Run dialog

   b. Type `sysdm.cpl ,3` and press Enter

   c. Click on the `Environment Variables` button
   
   d. Click the `New` button under the `User variables` section.

   e. Name the variable something that makes it clear what it is, like `RESSUB` for Resolve Subtitle Generator.

   f. Set the variable value to the full path of the Python script.

**Note:** You don't need to create an environment variable, but it prevents needing to explicitly define the full path in the next step (where I specify `%RESSUB%`).

2. I recommend setting the command line alias in Powershell since it's easy to permanently store.

   a. Open a Powershell shell.

   b. Open the profile file for editing. You can do this by running `notepad $PROFILE` in the shell. The path to the file being edited is `$PROFILE`. You can check the path by running `echo $PROFILE` in the shell.

   c. Add the following line to the file (assuming `ressub` is the name of the command you want to use globally):

   ```powershell
   function ressub { python "%RESSUB%\generate_srt.py" $args }
   ```

   d. Save the file and exit the text editor.

   e. Close and reopen the Powershell shell to apply the changes. It should work anywhere now.

#### **On Mac:**

1. Assuming you are using the default zsh shell, open the `.zshrc` file for editing.

   a. Run `nano ~/.zshrc` in the terminal. If you use VIM, you can use `vim ~/.zshrc` instead.

   b. Add the following line to the file (assuming `ressub` is the name of the command you want to use globally):

   ```zsh
   ressub() { python "/path/to/script/generate_srt.py" "$@" }
   ```
   
   c. Save the file and exit the text editor.

   d. Close and reopen the terminal to apply the changes. It should work anywhere now. You can restart zsh by running `exec zsh` in the ZSH shell.

#### **On Linux:**

1. Assuming you are using the default bash shell, open the `.bashrc` file for editing.

   a. Run `nano ~/.bashrc` in the terminal. If you use VIM, you can use `vim ~/.bashrc` instead.

   b. Add the following line to the file (assuming `ressub` is the name of the command you want to use globally):

   ```bash
   ressub() { python "/path/to/script/generate_srt.py" "$@" }
   ```
   
   c. Save the file and exit the text editor.

   d. Close and reopen the terminal to apply the changes. It should work anywhere now. You can restart bash by running `exec bash` in the bash shell.
   
## Audio/Video Conversion

If Resolve doesn't support the audio codec in your file (e.g. AAC in an M4A on Linux), you can convert it on the fly before importing using a `--<format>` flag. The converted file is temporary and the SRT is always saved next to the original source file.

```bash
# Convert a single M4A to WAV before importing
python generate_srt.py "episode.m4a" --wav

# Convert to a specific directory instead of temp
python generate_srt.py "episode.m4a" --wav "/path/to/output"

# Convert all M4A files to MP3 before importing
python generate_srt.py "samples/*.m4a" --mp3

# Mix converted and non-converted files in one command
python generate_srt.py "episode1.m4a" --wav "episode2.wav" "episode3.m4a" --mp3

# Convert audio track in a video file (e.g. AAC in MP4 unsupported on Linux — video stream is preserved, only audio is transcoded)
python generate_srt.py "recording.mp4" --mp3
```

### Supported conversion formats

| Flag | Format |
|------|--------|
| `--mp3` | MP3 |
| `--wav` | WAV |
| `--aac` | AAC |
| `--flac` | FLAC |
| `--opus` | Opus |
| `--ogg` | OGG Vorbis |
| `--aiff` | AIFF |

### Video container compatibility

For video files, only the audio stream is transcoded — the video is copied as-is. Not all audio formats work in every container:

| Container | Supported audio formats |
|-----------|------------------------|
| `.mp4` | `--mp3`, `--aac`, `--opus`, `--wav` |
| `.mov` | `--mp3`, `--aac`, `--wav` |
| `.mkv` | `--mp3`, `--aac`, `--wav`, `--flac`, `--opus` |
| `.avi` | `--mp3`, `--aac` |

Unsupported combinations are rejected with a clear error message listing what's allowed.

### ffmpeg Setup

ffmpeg is required for conversion flags. If it's not installed, the script will print an error. Install it using one of the following (these are common methods, not exhaustive):

- **Linux:** `sudo apt install ffmpeg` (or your distro's package manager equivalent)
- **macOS:** `brew install ffmpeg` (or https://ffmpeg.org/download.html)
- **Windows:** `winget install ffmpeg` (or https://ffmpeg.org/download.html)

### Setting a default conversion output directory

By default, converted files go to the system temp directory and are cleaned up on reboot. To always save conversions to a specific location instead, set a preference:

```bash
# Set a default conversion output directory (all aliases do the same thing)
python generate_srt.py --conv-dir "/my/output/path"
python generate_srt.py --conversion-dir "/my/output/path"
python generate_srt.py --set-conv-dir "/my/output/path"
python generate_srt.py --set-conversion-dir "/my/output/path"
python generate_srt.py --temp-dir "/my/output/path"
python generate_srt.py --tmp-dir "/my/output/path"

# Reset back to system temp
python generate_srt.py --conv-dir clear
python generate_srt.py --conv-dir temp
```

Once set, all conversions save to that directory automatically — no need to specify a path per-file. A per-file explicit path (e.g. `"episode.m4a" --wav "/some/path"`) still overrides the preference for that call. The preference is stored in `preferences.json` next to the script and only created when a non-default value is set. Relative paths are resolved to absolute at set time so the preference works correctly regardless of where you run the command from.

## Global Flags

These flags apply to the whole command rather than individual files and can be placed anywhere in the argument list.

| Flag | Description |
|------|-------------|
| `--concat` | Import all files into a single timeline instead of separate ones. Subtitles are generated across the entire timeline. Does not export an SRT by default — use with `--export` to save one. |
| `--export` | Write the SRT file. Redundant for normal per-file use (always exports), but required to export when using `--concat`. |
| `--import` | Import files into Resolve without generating subtitles. Works with and without `--concat`. Useful when you just need the conversion and import, not the subtitles. |

### Examples

```bash
# Import all M4A files into one timeline, generate subtitles in Resolve only (no SRT file)
python generate_srt.py "*.m4a" --wav --concat

# Same but also export the SRT next to the first file
python generate_srt.py "*.m4a" --wav --concat --export

# Generate subtitles in Resolve for a single file without exporting an SRT
python generate_srt.py "episode.m4a" --concat

# Convert AAC audio in an MP4 to MP3 and import into Resolve without generating subtitles
python generate_srt.py "recording.mp4" --mp3 --import

# Same but for multiple MP4s, all into one timeline
python generate_srt.py "*.mp4" --mp3 --import --concat
```

## Troubleshooting

If you encounter issues:
1. Ensure DaVinci Resolve is running and a project is open
2. Verify the environment variables are set correctly, which the program should let you define via user input if it isn't correct
3. Check that you have the required Python packages installed
4. Make sure you have write permissions in the output directory

### PyAudio Installation Issues on macOS

If you encounter issues installing PyAudio on macOS, try the following steps:

1. Install portaudio using Homebrew:
   ```bash
   brew install portaudio
   ```

2. If you're experiencing Python environment conflicts (especially with multiple Python versions installed), you may need to:
   
   a. Clear your PYTHONPATH environment variable temporarily:
   ```bash
   PYTHONPATH="" python -m pip install --upgrade pip
   PYTHONPATH="" python -m pip install -r requirements.txt
   ```
   
   b. If using pyenv or multiple Python installations, ensure you're using the correct pip for your Python version:
   ```bash
   python -m pip install -r requirements.txt
   ```
   
   instead of just using `pip install`.

3. If you get a "No module named '_audioop'" or "pyaudioop" error, try this direct installation approach which worked reliably:

   **For Python 3.7-3.9:**
   ```bash
   # First uninstall any existing PyAudio
   PYTHONPATH="" python -m pip uninstall -y pyaudio
   
   # Update pip, setuptools, and wheel
   PYTHONPATH="" python -m pip install --upgrade pip setuptools wheel
   
   # Install PyAudio with direct linking to portaudio
   PYTHONPATH="" pip install --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" pyaudio
   ```
   
   **For Python 3.13:**
   ```bash
   # Make sure to use the correct Python version
   python3.13 -m pip uninstall -y pyaudio
   
   # Update pip, setuptools, and wheel
   python3.13 -m pip install --upgrade pip setuptools wheel
   
   # Install PyAudio with direct linking to portaudio
   python3.13 -m pip install --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" pyaudio
   ```
   
   This forces pip to link against the Homebrew-installed portaudio library.
   
4. If you're using multiple Python versions on your system, ensure you're using the correct version for running the script:
   ```bash
   # For Python 3.13
   python3.13 generate_srt.py "your_audio_file.mp3"
   ```
   
   Also make sure your environment variables are set properly for the specific Python version you're using.

### PyDub/AudioOp Issues on Python 3.13

Python 3.13 removed the `audioop` module from the standard library, which PyDub depends on. This affects all platforms. Run the provided fix script:

```bash
python3 global_python_fix.py
```

**What the script does per platform:**

- **Linux** — installs `audioop-lts` (a maintained backport of `audioop` for Python 3.13+) via pip. You will be prompted before it runs `--break-system-packages`, which installs to your user packages (`~/.local/lib/...`) and is safe. If you prefer a virtual environment instead, the script will print guidance for that.
- **macOS** — reinstalls PyDub and creates compatibility shim modules for `audioop`.
- **Windows** — same as macOS.

**Known errors this fixes:**
```
ModuleNotFoundError: No module named 'audioop'
ModuleNotFoundError: No module named 'pyaudioop'
```

If you'd prefer to fix it manually on Linux without the script:
```bash
pip install --user --break-system-packages audioop-lts
```

If you still encounter issues after running the fix script, consider using a virtual environment with Python 3.11 or 3.12 which still include `audioop` natively.
