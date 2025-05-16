# Resolve Subtitle Generator

A Python script that generates SRT subtitle files from audio files using DaVinci Resolve's auto-captioning feature.

## Prerequisites

1. **DaVinci Resolve Studio** (version 18 or later)
2. **Python 3.6+** (64-bit version)
3. **Required Python packages** (install using `pip install -r requirements.txt`)

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
   function ressub { python "%RESSUB%\generate_srt.py" $args[0] }
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

### PyDub/AudioOp Issues on macOS with Python 3.13

If you're using Python 3.13 on macOS and encounter errors related to `audioop`, `_audioop`, or `pyaudioop` when importing PyDub, this is a known compatibility issue. Run the provided global Python fix script:

```bash
./global_python_fix.py
```

This script:
1. Reinstalls PyDub with the system Python 3.13
2. Creates compatibility modules (`_audioop.py`, `audioop.py`, and `pyaudioop.py`)
3. Tests that PyDub can be imported and used

The fix works by creating dummy implementations of the audio processing modules that PyDub expects but are missing or renamed in Python 3.13.

**After running the fix:**
- Use the global Python 3.13 interpreter to run your scripts:
  ```bash
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 generate_srt.py "your_audio_file.mp3"
  ```
- Make sure to use the full path to the Python 3.13 interpreter rather than relying on environment variables or aliases

**Known errors this fixes:**
```
ModuleNotFoundError: No module named 'audioop'
```
or
```
ModuleNotFoundError: No module named 'pyaudioop'
```

**Note:** The fix adds dummy implementations of the audio operations modules, which should be sufficient for basic PyDub functionality but may not work for all advanced audio processing operations.

If you still encounter issues after running the fix script, consider downgrading to Python 3.9 which has better compatibility with audio processing libraries.