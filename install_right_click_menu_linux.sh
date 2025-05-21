#!/bin/bash

echo "Setting up DaVinci Resolve Subtitle Generator context menu for Linux..."
echo

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="${SCRIPT_DIR}/generate_srt.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: generate_srt.py script not found at: $PYTHON_SCRIPT"
    echo "Make sure you're running this from the correct directory."
    exit 1
fi

# Find Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

echo "Using Python: $PYTHON"
echo "Script path: $PYTHON_SCRIPT"

# Create the wrapper script that will be called by the file managers
WRAPPER_SCRIPT="${SCRIPT_DIR}/linux_subtitle_handler.sh"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="\${SCRIPT_DIR}/generate_srt.py"

# Find Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    zenity --error --text="Python not found. Please install Python 3."
    exit 1
fi

# Check if script exists
if [ ! -f "\$PYTHON_SCRIPT" ]; then
    zenity --error --text="Cannot find generate_srt.py script. Please reinstall."
    exit 1
fi

# Process files
echo "Processing \$# files with DaVinci Resolve Subtitle Generator..."
echo "Using Python: \$PYTHON"
echo "Script path: \$PYTHON_SCRIPT"
echo

# Log all files being processed
echo "Files to process:" > "\${SCRIPT_DIR}/linux_subtitle_log.txt"
for file in "\$@"; do
    echo "  \$file" >> "\${SCRIPT_DIR}/linux_subtitle_log.txt"
done

# Run the Python script with all files as arguments
"\$PYTHON" "\$PYTHON_SCRIPT" "\$@" 2>&1 | tee -a "\${SCRIPT_DIR}/linux_subtitle_log.txt"

# Check exit code
exit_code=\${PIPESTATUS[0]}
if [ \$exit_code -ne 0 ]; then
    zenity --error --text="Error generating subtitles. Check the log file for details."
    exit \$exit_code
else
    zenity --info --text="Subtitle generation completed successfully!"
fi
EOF

# Make the wrapper script executable
chmod +x "$WRAPPER_SCRIPT"
echo "Created wrapper script: $WRAPPER_SCRIPT"

# Set up for Nautilus (GNOME)
echo "Setting up Nautilus (GNOME) integration..."
NAUTILUS_SCRIPTS_DIR="${HOME}/.local/share/nautilus/scripts"

# Create the scripts directory if it doesn't exist
mkdir -p "$NAUTILUS_SCRIPTS_DIR"

# Create the Nautilus script
NAUTILUS_SCRIPT="${NAUTILUS_SCRIPTS_DIR}/Generate Subtitles with DaVinci Resolve"

cat > "$NAUTILUS_SCRIPT" << EOF
#!/bin/bash
"$WRAPPER_SCRIPT" "\$@"
EOF

# Make the Nautilus script executable
chmod +x "$NAUTILUS_SCRIPT"
echo "Created Nautilus script: $NAUTILUS_SCRIPT"

# Set up for Thunar (XFCE)
echo "Setting up Thunar (XFCE) integration..."
THUNAR_ACTIONS_DIR="${HOME}/.config/Thunar/uca.xml"

# Create parent directory if it doesn't exist
mkdir -p "${HOME}/.config/Thunar"

# Check if uca.xml exists
if [ ! -f "$THUNAR_ACTIONS_DIR" ]; then
    # Create a new uca.xml file
    cat > "$THUNAR_ACTIONS_DIR" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<actions>
  <action>
    <icon>applications-multimedia</icon>
    <name>Generate Subtitles with DaVinci Resolve</name>
    <command>$WRAPPER_SCRIPT %F</command>
    <description>Generate subtitles for audio/video files</description>
    <patterns>*.mp3;*.wav;*.aac;*.flac;*.ogg;*.m4a;*.mp4;*.mov;*.mkv;*.avi;*.wmv;*.m4v;*.mts</patterns>
    <audio-files/>
    <video-files/>
    <other-files/>
  </action>
</actions>
EOF
    echo "Created new Thunar uca.xml file"
else
    # Check if the action already exists
    if grep -q "Generate Subtitles with DaVinci Resolve" "$THUNAR_ACTIONS_DIR"; then
        echo "Thunar action already exists, updating..."
        # Use sed to update the existing action
        sed -i "/<name>Generate Subtitles with DaVinci Resolve<\/name>/,/<command>.*<\/command>/ s|<command>.*</command>|<command>$WRAPPER_SCRIPT %F</command>|" "$THUNAR_ACTIONS_DIR"
    else
        echo "Adding new Thunar action..."
        # Insert the new action before the closing </actions> tag
        sed -i "s|</actions>|  <action>\n    <icon>applications-multimedia</icon>\n    <name>Generate Subtitles with DaVinci Resolve</name>\n    <command>$WRAPPER_SCRIPT %F</command>\n    <description>Generate subtitles for audio/video files</description>\n    <patterns>*.mp3;*.wav;*.aac;*.flac;*.ogg;*.m4a;*.mp4;*.mov;*.mkv;*.avi;*.wmv;*.m4v;*.mts</patterns>\n    <audio-files/>\n    <video-files/>\n    <other-files/>\n  </action>\n</actions>|" "$THUNAR_ACTIONS_DIR"
    fi
fi

# Set up for Dolphin (KDE)
echo "Setting up Dolphin (KDE) integration..."
DOLPHIN_DIR="${HOME}/.local/share/kservices5/ServiceMenus"

# Create the directory if it doesn't exist
mkdir -p "$DOLPHIN_DIR"

# Create the Dolphin service menu file
DOLPHIN_FILE="${DOLPHIN_DIR}/generate_subtitles.desktop"

cat > "$DOLPHIN_FILE" << EOF
[Desktop Entry]
Type=Service
X-KDE-ServiceTypes=KonqPopupMenu/Plugin
MimeType=audio/mpeg;audio/mp4;audio/wav;audio/ogg;audio/flac;video/mp4;video/x-matroska;video/quicktime;video/x-msvideo;video/x-ms-wmv;
Actions=GenerateSubtitles
X-KDE-Priority=TopLevel

[Desktop Action GenerateSubtitles]
Name=Generate Subtitles with DaVinci Resolve
Icon=applications-multimedia
Exec="$WRAPPER_SCRIPT" %F
EOF

echo "Created Dolphin service menu: $DOLPHIN_FILE"

# Create uninstall script
UNINSTALL_SCRIPT="${SCRIPT_DIR}/uninstall_right_click_menu_linux.sh"

cat > "$UNINSTALL_SCRIPT" << EOF
#!/bin/bash

echo "Removing DaVinci Resolve Subtitle Generator context menu for Linux..."

# Remove Nautilus script
NAUTILUS_SCRIPT="\${HOME}/.local/share/nautilus/scripts/Generate Subtitles with DaVinci Resolve"
if [ -f "\$NAUTILUS_SCRIPT" ]; then
    echo "Removing Nautilus script..."
    rm -f "\$NAUTILUS_SCRIPT"
    echo "Nautilus script removed."
else
    echo "Nautilus script not found, nothing to remove."
fi

# Remove Thunar action
THUNAR_ACTIONS_DIR="\${HOME}/.config/Thunar/uca.xml"
if [ -f "\$THUNAR_ACTIONS_DIR" ] && grep -q "Generate Subtitles with DaVinci Resolve" "\$THUNAR_ACTIONS_DIR"; then
    echo "Removing Thunar action..."
    # Create a temporary file without the action
    grep -v -A 10 -B 1 "Generate Subtitles with DaVinci Resolve" "\$THUNAR_ACTIONS_DIR" | grep -v -A 1 -B 10 "Generate subtitles for audio/video files" > "\${THUNAR_ACTIONS_DIR}.tmp"
    # Fix any XML issues that might have been created by the grep removal
    sed -i 's|<action>  </action>||g' "\${THUNAR_ACTIONS_DIR}.tmp"
    sed -i 's|<actions>  </actions>|<actions></actions>|g' "\${THUNAR_ACTIONS_DIR}.tmp"
    sed -i '/^$/d' "\${THUNAR_ACTIONS_DIR}.tmp"
    # Replace the original file
    mv "\${THUNAR_ACTIONS_DIR}.tmp" "\$THUNAR_ACTIONS_DIR"
    echo "Thunar action removed."
else
    echo "Thunar action not found, nothing to remove."
fi

# Remove Dolphin service menu
DOLPHIN_FILE="\${HOME}/.local/share/kservices5/ServiceMenus/generate_subtitles.desktop"
if [ -f "\$DOLPHIN_FILE" ]; then
    echo "Removing Dolphin service menu..."
    rm -f "\$DOLPHIN_FILE"
    echo "Dolphin service menu removed."
else
    echo "Dolphin service menu not found, nothing to remove."
fi

# Remove wrapper script
WRAPPER_SCRIPT="\${HOME}/linux_subtitle_handler.sh"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WRAPPER_SCRIPT="\${SCRIPT_DIR}/linux_subtitle_handler.sh"
if [ -f "\$WRAPPER_SCRIPT" ]; then
    echo "Removing wrapper script..."
    rm -f "\$WRAPPER_SCRIPT"
    echo "Wrapper script removed."
else
    echo "Wrapper script not found, nothing to remove."
fi

# Remove log file
LOG_FILE="\${SCRIPT_DIR}/linux_subtitle_log.txt"
if [ -f "\$LOG_FILE" ]; then
    echo "Removing log file..."
    rm -f "\$LOG_FILE"
    echo "Log file removed."
fi

echo "Uninstallation complete. You may need to restart your file manager for changes to take effect."
EOF

# Make the uninstall script executable
chmod +x "$UNINSTALL_SCRIPT"

echo "Installation complete!"
echo
echo "You can now right-click on audio and video files and select:"
echo "  - In Nautilus (GNOME): Right-click -> Scripts -> Generate Subtitles with DaVinci Resolve"
echo "  - In Thunar (XFCE): Right-click -> Generate Subtitles with DaVinci Resolve"
echo "  - In Dolphin (KDE): Right-click -> Actions -> Generate Subtitles with DaVinci Resolve"
echo
echo "To remove the context menu entries, run the uninstall_right_click_menu_linux.sh script."
echo
echo "Note: You may need to restart your file manager for the changes to take effect."

exit 0 