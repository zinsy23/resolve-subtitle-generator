#!/bin/bash

echo "Removing context menu for DaVinci Resolve Subtitle Generator on Linux..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_subtitle_generator.sh"

# Remove Nautilus script
NAUTILUS_SCRIPT_PATH="$HOME/.local/share/nautilus/scripts/Generate Subtitles with DaVinci Resolve"
if [ -f "$NAUTILUS_SCRIPT_PATH" ]; then
    echo "Removing Nautilus script..."
    rm -f "$NAUTILUS_SCRIPT_PATH"
    echo "Nautilus script removed successfully"
else
    echo "Nautilus script not found (already removed)"
fi

# Remove file-manager action desktop file
ACTIONS_DESKTOP_FILE="$HOME/.local/share/file-manager/actions/generate-subtitles.desktop"
if [ -f "$ACTIONS_DESKTOP_FILE" ]; then
    echo "Removing file-manager action..."
    rm -f "$ACTIONS_DESKTOP_FILE"
    echo "File-manager action removed successfully"
else
    echo "File-manager action not found (already removed)"
fi

# Remove Thunar custom action
THUNAR_CONFIG_FILE="$HOME/.config/Thunar/uca.xml"
if [ -f "$THUNAR_CONFIG_FILE" ]; then
    if grep -q "Generate Subtitles with DaVinci Resolve" "$THUNAR_CONFIG_FILE"; then
        echo "Removing Thunar custom action..."
        # Make a backup
        cp "$THUNAR_CONFIG_FILE" "$THUNAR_CONFIG_FILE.bak"
        
        # Create a new file without our action
        grep -v -A6 -B1 "Generate Subtitles with DaVinci Resolve" "$THUNAR_CONFIG_FILE" | grep -v "^\-\-$" > "$THUNAR_CONFIG_FILE.tmp"
        
        # Replace the original file
        mv "$THUNAR_CONFIG_FILE.tmp" "$THUNAR_CONFIG_FILE"
        echo "Thunar custom action removed successfully"
    else
        echo "Thunar custom action not found (already removed)"
    fi
else
    echo "Thunar configuration not found"
fi

# Remove the wrapper script
if [ -f "$WRAPPER_SCRIPT" ]; then
    echo "Removing wrapper script..."
    rm -f "$WRAPPER_SCRIPT"
    echo "Wrapper script removed successfully"
else
    echo "Wrapper script not found (already removed)"
fi

echo "Context menu entries removed successfully!"
echo "You may need to restart your file manager for the changes to take effect." 