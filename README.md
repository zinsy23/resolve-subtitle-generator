# Resolve Subtitle Generator

A Python script that generates SRT subtitle files from audio files using DaVinci Resolve's auto-captioning feature.

## Prerequisites

1. **DaVinci Resolve Studio** (version 18 or later)
2. **Python 3.6+** (64-bit version)
3. **Required Python packages** (install using `pip install -r requirements.txt`)

## Environment Setup

Before running the script, you need to set up the following environment variables (figure out your paths if necessary):

### Windows
```powershell
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
$env:RESOLVE_SCRIPT_LIB = "C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
$env:PYTHONPATH = "$env:PYTHONPATH;$env:RESOLVE_SCRIPT_API\Modules"
```

**Note**: You may consider making it permantent by going to `sysdm.cpl` and changing user environment variables from there. Set those three variables above to their values.

### macOS
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules"
```

**Note**: You can permanently set environment variables in macOS by adding them to your shell configuration file (e.g., `~/.bash_profile`, `~/.zshrc`, or `~/.bashrc`). Add the following lines to the file:

### Linux
```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules"
```

**Note**: To permanently set environment variables in Linux, you can add them to your shell configuration file. For example, you can add the following lines to your `~/.bashrc` or `~/.bash_profile` file:


## Usage

1. **Start DaVinci Resolve** and create a new project or open an existing one. It won't work without Resolve running as it still uses the UI for functionality, but still fortunately in an automated way.
2. **Run the script** with one or more audio files as arguments:

```bash
# Process a single file
python generate_srt.py "path/to/your/audio.mp3"

# Process multiple files
python generate_srt.py "audio1.mp3" "audio2.mp3" "audio3.mp3"

# Process all MP3 files in a directory
python generate_srt.py "samples/*.MP3"
```

The script will:
1. Create a timeline for each audio file
2. Generate subtitles using Resolve's auto-captioning
3. Export the subtitles as SRT files in the same directory as the input files

## Output

For each input audio file, a corresponding SRT file will be created in the same directory with the same name (but with .srt extension). For example:
- Input: `samples/audio1.mp3`
- Output: `samples/audio1.srt`

## Notes

- The script requires DaVinci Resolve to be running and a project to be open
- The script will create timelines in the current project
- Audio files should be in a format supported by DaVinci Resolve (MP3, WAV, etc.)
- The generated SRT files include bold formatting and proper line breaks
- The version of my script does my typical preferred settings, so you may consider modifying the `create_subtitles_from_audio()` function in generate_srt.py to match your settings. 
    - I haven't tested single line SRT creation yet since it has linebreak logic in it for double lines
- I generated this program using AI until it did my desired behavior, so please excuse any brevity in this project since I'm more concerned about being able to use it as a tool for myself.

## Troubleshooting

If you encounter issues:
1. Ensure DaVinci Resolve is running and a project is open
2. Verify the environment variables are set correctly
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