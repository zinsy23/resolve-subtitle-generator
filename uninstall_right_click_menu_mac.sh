#!/bin/bash

echo "Removing context menu for DaVinci Resolve Subtitle Generator on macOS..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_subtitle_generator.sh"

# Remove the Automator service
WORKFLOW_PATH="$HOME/Library/Services/Generate Subtitles.workflow"
if [ -d "$WORKFLOW_PATH" ]; then
    echo "Removing Automator service..."
    rm -rf "$WORKFLOW_PATH"
    echo "Automator service removed successfully"
else
    echo "Automator service not found (already removed)"
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
echo "You may need to restart Finder for the changes to take effect." 