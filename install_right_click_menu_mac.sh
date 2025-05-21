#!/bin/bash

echo "Setting up context menu for DaVinci Resolve Subtitle Generator on macOS..."

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

# Create an Automator Quick Action
WORKFLOW_DIR="$HOME/Library/Services"
mkdir -p "$WORKFLOW_DIR"

WORKFLOW_NAME="Generate Subtitles.workflow"
WORKFLOW_PATH="$WORKFLOW_DIR/$WORKFLOW_NAME"

# Remove existing workflow if it exists
if [ -d "$WORKFLOW_PATH" ]; then
    rm -rf "$WORKFLOW_PATH"
fi

# Create the workflow directory structure
mkdir -p "$WORKFLOW_PATH/Contents/document.wflow"

# Create the Info.plist file
cat > "$WORKFLOW_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Generate Subtitles with DaVinci Resolve</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.audio</string>
                <string>public.movie</string>
                <string>public.mpeg-4</string>
                <string>public.avi</string>
                <string>com.apple.quicktime-movie</string>
                <string>org.matroska.mkv</string>
                <string>com.microsoft.windows-media-wmv</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# Create the workflow file
cat > "$WORKFLOW_PATH/Contents/document.wflow" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>492</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>1.0.2</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>fileNames</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>"$WRAPPER_SCRIPT" "$@"</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
            </dict>
        </dict>
    </array>
</dict>
</plist>
EOF

echo "Context menu setup completed successfully!"
echo "You can now right-click on audio and video files in Finder and select 'Generate Subtitles with DaVinci Resolve'"
echo "from the Services menu."
echo "If you already had the context menu installed, the previous version has been updated." 