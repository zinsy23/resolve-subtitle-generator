@echo off
echo Setting up context menu for DaVinci Resolve Subtitle Generator...

:: Get the full path of the generate_srt.py script
set "SCRIPT_PATH=%~dp0generate_srt.py"
set "PYTHON_EXE=python"

:: Verify Python is installed and available
%PYTHON_EXE% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found. Please make sure Python is installed and in your PATH.
    pause
    exit /b 1
)

:: Create registry entries for right-click on audio files
echo Adding context menu for audio files...
reg add "HKEY_CURRENT_USER\Software\Classes\.mp3\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mp3\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mp3\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.wav\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.wav\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.wav\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

:: Add support for video file formats
echo Adding context menu for video files...
reg add "HKEY_CURRENT_USER\Software\Classes\.mp4\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mp4\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mp4\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.mov\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mov\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mov\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.wmv\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.wmv\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.wmv\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.avi\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.avi\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.avi\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.mkv\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mkv\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mkv\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

:: Add more video formats
reg add "HKEY_CURRENT_USER\Software\Classes\.mts\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mts\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.mts\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

reg add "HKEY_CURRENT_USER\Software\Classes\.m4v\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.m4v\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\.m4v\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

:: Also add for file selection in general (works when multiple files are selected)
echo Adding context menu for file selection...
reg add "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /v "MultiSelectModel" /t REG_SZ /d "Player" /f
reg add "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT\command" /t REG_SZ /d "%PYTHON_EXE% \"%SCRIPT_PATH%\" \"%%1\"" /f

echo Context menu setup completed successfully!
echo You can now right-click on audio and video files to generate subtitles.
pause 