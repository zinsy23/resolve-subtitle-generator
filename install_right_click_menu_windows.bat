@echo off
setlocal EnableDelayedExpansion

:: Check if running as administrator
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% NEQ 0 (
    echo This script requires administrator privileges.
    echo Please run this script as administrator.
    echo Right-click the script and select "Run as administrator".
    pause
    exit /b 1
)

echo Setting up context menu for DaVinci Resolve Subtitle Generator...

:: Get the full path of the generate_srt.py script
set "SCRIPT_PATH=%~dp0generate_srt.py"

:: Try to get the full path to Python
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_EXE=%%i"
    goto python_found
)
set "PYTHON_EXE=python"
:python_found

echo Using Python: %PYTHON_EXE%

:: Verify Python is installed and available
"%PYTHON_EXE%" --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found. Please make sure Python is installed and in your PATH.
    pause
    exit /b 1
)

:: Run a test to verify script exists and is accessible
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Script not found: %SCRIPT_PATH%
    pause
    exit /b 1
)

:: First remove existing context menu entries for clean install
echo Removing any existing context menu entries for clean installation...
:: Remove older registry entries
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRT" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRTMulti" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSubtitles" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\*\shell\DaVinciSubs" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /f >nul 2>&1

:: Remove from user registry as well
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRTMulti" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSubtitles" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\DaVinciSubs" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\audio\shell\DaVinciSubs" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\video\shell\DaVinciSubs" /f >nul 2>&1

:: Create the samples directory if it doesn't exist
mkdir "%~dp0samples" 2>nul

:: Use the all-in-one handler script path
set "HANDLER_SCRIPT=%~dp0subtitle_handler.bat"

echo.
echo Adding context menu entries for the handler script...

:: Define the launcher command that uses the handler script
set "LAUNCHER=cmd.exe /c \"%HANDLER_SCRIPT%\" \"%%1\""

:: Add to SystemFileAssociations for audio and video files
echo Adding to audio file types...
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /ve /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /v "MultiSelectModel" /t REG_SZ /d "Player" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs\command" /ve /t REG_SZ /d "%LAUNCHER%" /f

echo Adding to video file types...
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /ve /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /v "MultiSelectModel" /t REG_SZ /d "Player" /f
reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs\command" /ve /t REG_SZ /d "%LAUNCHER%" /f

:: Add the main context menu entry for file extensions
echo Adding specific file extension entries...

:: List of extensions to add
set "audio_exts=.mp3 .wav .aac .flac .ogg .m4a"
set "video_exts=.mp4 .mov .mkv .avi .wmv .m4v .mts"

:: Register each extension
for %%E in (%audio_exts% %video_exts%) do (
    echo Adding for %%E files...
    reg add "HKEY_CLASSES_ROOT\%%E\shell\DaVinciSubs" /ve /t REG_SZ /d "Generate Subtitles with DaVinci Resolve" /f
    reg add "HKEY_CLASSES_ROOT\%%E\shell\DaVinciSubs" /v "Icon" /t REG_SZ /d "%PYTHON_EXE%,0" /f
    reg add "HKEY_CLASSES_ROOT\%%E\shell\DaVinciSubs" /v "MultiSelectModel" /t REG_SZ /d "Player" /f
    reg add "HKEY_CLASSES_ROOT\%%E\shell\DaVinciSubs\command" /ve /t REG_SZ /d "%LAUNCHER%" /f
)

:: Create uninstall script
set "UNINSTALL_SCRIPT=%~dp0uninstall_right_click_menu_windows.bat"

echo @echo off > "%UNINSTALL_SCRIPT%"
echo setlocal EnableDelayedExpansion >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo :: Check if running as administrator >> "%UNINSTALL_SCRIPT%"
echo ^>nul 2^>^&1 "%%SYSTEMROOT%%\system32\cacls.exe" "%%SYSTEMROOT%%\system32\config\system" >> "%UNINSTALL_SCRIPT%"
echo if %%errorlevel%% NEQ 0 ( >> "%UNINSTALL_SCRIPT%"
echo     echo This script requires administrator privileges. >> "%UNINSTALL_SCRIPT%"
echo     echo Please run this script as administrator. >> "%UNINSTALL_SCRIPT%"
echo     echo Right-click the script and select "Run as administrator". >> "%UNINSTALL_SCRIPT%"
echo     pause >> "%UNINSTALL_SCRIPT%"
echo     exit /b 1 >> "%UNINSTALL_SCRIPT%"
echo ) >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo echo Removing context menu for DaVinci Resolve Subtitle Generator... >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo :: Remove registry entries >> "%UNINSTALL_SCRIPT%"
echo echo Removing registry entries... >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSubtitles" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRT" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRTMulti" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\*\shell\DaVinciSubs" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /f >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSubtitles" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRTMulti" /f >> "%UNINSTALL_SCRIPT%"
echo reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\DaVinciSubs" /f >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo :: Remove specific file extensions >> "%UNINSTALL_SCRIPT%"
echo set "extensions=.mp3 .wav .aac .flac .ogg .m4a .mp4 .mov .mkv .avi .wmv .m4v .mts" >> "%UNINSTALL_SCRIPT%"
echo for %%%%E in (%%extensions%%) do ( >> "%UNINSTALL_SCRIPT%"
echo     reg delete "HKEY_CLASSES_ROOT\%%%%E\shell\DaVinciSubs" /f >> "%UNINSTALL_SCRIPT%"
echo ) >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo :: Delete wrapper scripts >> "%UNINSTALL_SCRIPT%"
echo set "SCRIPTS=%%~dp0subtitle_handler.bat %%~dp0file_collector.bat %%~dp0run_subtitle_generator.bat %%~dp0run_subtitle_generator.vbs %%~dp0selected_files.txt %%~dp0.processing" >> "%UNINSTALL_SCRIPT%"
echo for %%%%F in (%%SCRIPTS%%) do ( >> "%UNINSTALL_SCRIPT%"
echo     if exist "%%%%F" ( >> "%UNINSTALL_SCRIPT%"
echo         echo Removing %%%%~nxF... >> "%UNINSTALL_SCRIPT%"
echo         del "%%%%F" >> "%UNINSTALL_SCRIPT%"
echo     ) >> "%UNINSTALL_SCRIPT%"
echo ) >> "%UNINSTALL_SCRIPT%"
echo. >> "%UNINSTALL_SCRIPT%"
echo echo Context menu entries removed successfully! >> "%UNINSTALL_SCRIPT%"
echo echo You may need to restart Explorer for the changes to take effect. >> "%UNINSTALL_SCRIPT%"
echo echo. >> "%UNINSTALL_SCRIPT%"
echo echo To restart Explorer now, type Y and press Enter. >> "%UNINSTALL_SCRIPT%"
echo set /p restart_now=Restart Explorer now? [Y/N]: >> "%UNINSTALL_SCRIPT%"
echo if /i "%%restart_now%%" == "Y" ( >> "%UNINSTALL_SCRIPT%"
echo     echo Restarting Explorer... >> "%UNINSTALL_SCRIPT%"
echo     taskkill /f /im explorer.exe >> "%UNINSTALL_SCRIPT%"
echo     start explorer.exe >> "%UNINSTALL_SCRIPT%"
echo ) >> "%UNINSTALL_SCRIPT%"
echo pause >> "%UNINSTALL_SCRIPT%"

echo.
echo Context menu setup completed successfully!
echo.
echo You can now right-click on audio and video files and select:
echo "Generate Subtitles with DaVinci Resolve"
echo.
echo This uses a completely different approach:
echo 1. Each selected file is seamlessly added to a collection
echo 2. After a short delay, a single window opens to process all files
echo 3. All files are processed in a single Python command
echo.
echo Important: No windows will appear when you first select files.
echo After about 1 second, a single command window will open with all files.
echo.
echo To restart Explorer now and apply changes immediately, type Y and press Enter.
set /p restart_now=Restart Explorer now? [Y/N]: 
if /i "%restart_now%" == "Y" (
    echo Restarting Explorer...
    taskkill /f /im explorer.exe
    start explorer.exe
)
echo.
pause 