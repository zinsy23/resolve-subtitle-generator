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
 
echo Removing context menu for DaVinci Resolve Subtitle Generator... 
 
:: Remove registry entries 
echo Removing registry entries... 
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSubtitles" /f 
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRT" /f 
reg delete "HKEY_CLASSES_ROOT\*\shell\GenerateSRTMulti" /f 
reg delete "HKEY_CLASSES_ROOT\*\shell\DaVinciSubs" /f 
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\audio\shell\DaVinciSubs" /f 
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\video\shell\DaVinciSubs" /f 
 
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSubtitles" /f 
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRT" /f 
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\GenerateSRTMulti" /f 
reg delete "HKEY_CURRENT_USER\Software\Classes\*\shell\DaVinciSubs" /f 
 
:: Remove specific file extensions 
set "extensions=.mp3 .wav .aac .flac .ogg .m4a .mp4 .mov .mkv .avi .wmv .m4v .mts" 
for %%E in (%extensions%) do ( 
    reg delete "HKEY_CLASSES_ROOT\%%E\shell\DaVinciSubs" /f 
) 
 
:: Delete wrapper scripts 
set "SCRIPTS=%~dp0subtitle_handler.bat %~dp0file_collector.bat %~dp0run_subtitle_generator.bat %~dp0run_subtitle_generator.vbs %~dp0selected_files.txt %~dp0.processing" 
for %%F in (%SCRIPTS%) do ( 
    if exist "%%F" ( 
        echo Removing %%~nxF... 
        del "%%F" 
    ) 
) 
 
echo Context menu entries removed successfully 
echo You may need to restart Explorer for the changes to take effect. 
echo. 
echo To restart Explorer now, type Y and press Enter. 
set /p restart_now=Restart Explorer now? [Y/N]: 
if /i "%restart_now%" == "Y" ( 
    echo Restarting Explorer... 
    taskkill /f /im explorer.exe 
    start explorer.exe 
) 
pause 
