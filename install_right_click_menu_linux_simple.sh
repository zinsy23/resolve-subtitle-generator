#!/bin/bash

echo "Setting up context menu for DaVinci Resolve Subtitle Generator on Linux..."

# Get the directory of this script and the full path to generate_srt.py
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GENERATE_SCRIPT="$SCRIPT_DIR/generate_srt.py"

# Make sure generate_srt.py exists
if [ ! -f "$GENERATE_SCRIPT" ]; then
    echo "Error: $GENERATE_SCRIPT not found!"
    exit 1
fi

# Make sure the script is executable
chmod +x "$GENERATE_SCRIPT"

# Create a wrapper script that will actually run the Python script
WRAPPER_SCRIPT="$SCRIPT_DIR/run_subtitle_generator.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Wrapper script for running the Subtitle Generator

# Get the directory of this script
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
GENERATE_SCRIPT="\$SCRIPT_DIR/generate_srt.py"

# Check if files were provided
if [ \$# -eq 0 ]; then
    echo "Error: No files specified"
    exit 1
fi

# Print the selected files
echo "Running DaVinci Resolve Subtitle Generator..."
echo "Selected files: \$@"

# Run the Python script with all files as arguments
cd "\$SCRIPT_DIR"
python "\$GENERATE_SCRIPT" "\$@"

# Check if the script ran successfully
if [ \$? -ne 0 ]; then
    echo "Error: The script encountered an error."
    exit 1
fi

echo "Subtitle generation completed."
EOF

# Make the wrapper script executable
chmod +x "$WRAPPER_SCRIPT"

# Create Nautilus Scripts directory if it doesn't exist
NAUTILUS_SCRIPTS_DIR="$HOME/.local/share/nautilus/scripts"
mkdir -p "$NAUTILUS_SCRIPTS_DIR"

# Create the script
SCRIPT_NAME="Generate Subtitles with DaVinci Resolve"
NAUTILUS_SCRIPT_PATH="$NAUTILUS_SCRIPTS_DIR/$SCRIPT_NAME"

cat > "$NAUTILUS_SCRIPT_PATH" << EOF
#!/bin/bash
# This script processes selected audio and video files through DaVinci Resolve's subtitle generator

# Build a list of valid media files
valid_files=()

for file in \$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS; do
    # Check if file is an audio or video file by extension
    file_lower=\$(echo "\$file" | tr '[:upper:]' '[:lower:]')
    if [[ "\$file_lower" =~ \.(mp3|wav|mp4|mkv|avi|mov|wmv|m4v|mts)\$ ]]; then
        valid_files+=("\$file")
    fi
done

if [ \${#valid_files[@]} -eq 0 ]; then
    zenity --error --text="No valid audio or video files selected." --title="DaVinci Resolve Subtitle Generator"
    exit 1
fi

# Process all files in a single call
"$WRAPPER_SCRIPT" "\${valid_files[@]}"
EOF

# Make the script executable
chmod +x "$NAUTILUS_SCRIPT_PATH"

# Create .desktop file for right-click menu in newer Nautilus versions (Nautilus Actions)
ACTIONS_DIR="$HOME/.local/share/file-manager/actions"
mkdir -p "$ACTIONS_DIR"

cat > "$ACTIONS_DIR/generate-subtitles.desktop" << EOF
[Desktop Entry]
Type=Action
Name=Generate Subtitles with DaVinci Resolve
Tooltip=Generate subtitles using DaVinci Resolve
Icon=applications-multimedia
Profiles=audio_video;

[X-Action-Profile audio_video]
MimeTypes=audio/mpeg;audio/wav;audio/x-wav;audio/mp3;video/mp4;video/x-matroska;video/avi;video/quicktime;video/x-ms-wmv;video/mpeg;video/x-m4v;
Exec="$WRAPPER_SCRIPT" %F
EOF

echo ""
echo "Context menu setup completed successfully for Nautilus/GNOME Files!"
echo "You can now right-click on audio and video files and select:"
echo "Scripts → Generate Subtitles with DaVinci Resolve"
echo ""
echo "For Thunar (XFCE) users, please set up the custom action manually:"
echo "1. Open Thunar file manager"
echo "2. Go to Edit → Configure custom actions..."
echo "3. Click the + button to add a new action"
echo "4. Enter these details:"
echo "   - Name: Generate Subtitles with DaVinci Resolve"
echo "   - Command: \"$WRAPPER_SCRIPT\" %F"
echo "   - Icon: applications-multimedia (or your choice)"
echo "5. In the Appearance Conditions tab, select these file patterns:"
echo "   *.mp3;*.MP3;*.wav;*.WAV;*.mp4;*.MP4;*.mkv;*.MKV;*.avi;*.AVI;*.mov;*.MOV;*.wmv;*.WMV;*.m4v;*.M4V;*.mts;*.MTS"
echo ""
echo "Note: You may need to restart your file manager for changes to take effect."
echo "If you already had the context menu installed, the previous version has been updated." 