#!/bin/bash

echo "Setting up DaVinci Resolve Subtitle Generator context menu for macOS..."
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

# Ensure Service directory exists
SERVICES_DIR="${HOME}/Library/Services"
mkdir -p "$SERVICES_DIR"

# Create a workflow file for audio/video files
WORKFLOW_DIR="${SERVICES_DIR}/Generate Subtitles.workflow"
CONTENTS_DIR="${WORKFLOW_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Remove old service if it exists
if [ -d "$WORKFLOW_DIR" ]; then
    echo "Removing existing service..."
    rm -rf "$WORKFLOW_DIR"
fi

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << EOF
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
            <string>runWorkflowServiceForFiles</string>
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
                <string>public.mp3</string>
                <string>public.wav</string>
                <string>public.aac-audio</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# Create document.wflow
cat > "${CONTENTS_DIR}/document.wflow" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>509</string>
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
                <string>2.1</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>#!/bin/bash

# Get paths to selected files
files=("$@")

# Check if any files were passed
if [ \${#files[@]} -eq 0 ]; then
    echo "Error: No files selected"
    exit 1
fi

# Path to the Python script
SCRIPT_PATH="$PYTHON_SCRIPT"

# Find Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    osascript -e 'display dialog "Python not found. Please install Python 3." buttons {"OK"} default button "OK" with icon stop with title "Error"'
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    osascript -e 'display dialog "Cannot find generate_srt.py script. Please reinstall." buttons {"OK"} default button "OK" with icon stop with title "Error"'
    exit 1
fi

# Process files
echo "Processing \${#files[@]} files with DaVinci Resolve Subtitle Generator..."
echo "Using Python: $PYTHON"
echo "Script path: $SCRIPT_PATH"
echo

# Convert file array to command arguments
file_args=""
for file in "\${files[@]}"; do
    file_args+="\"$file\" "
    echo "File: $file"
done

# Run the script with all files
CMD="$PYTHON \"$SCRIPT_PATH\" $file_args"
echo "Executing: $CMD"
echo

# Execute command
eval $CMD

# Check exit code
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "Error generating subtitles. Check Terminal for details." buttons {"OK"} default button "OK" with icon stop with title "Error"'
else
    osascript -e 'display dialog "Subtitle generation completed successfully!" buttons {"OK"} default button "OK" with title "Success"'
fi
</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>98F7F2BB-4C5D-47A8-B41F-4A42D9DD7C68</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>D8F9A61C-A8F5-45F0-813B-0323F0AB6A0A</string>
                <key>UUID</key>
                <string>5A0EDEC2-4A32-4D6B-810F-7A239FEE9A4D</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <string>/bin/sh</string>
                        <key>name</key>
                        <string>shell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                    <key>1</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>1</string>
                    </dict>
                    <key>2</key>
                    <dict>
                        <key>default value</key>
                        <false/>
                        <key>name</key>
                        <string>CheckedForUserDefaultShell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>2</string>
                    </dict>
                    <key>3</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>3</string>
                    </dict>
                    <key>4</key>
                    <dict>
                        <key>default value</key>
                        <integer>0</integer>
                        <key>name</key>
                        <string>inputMethod</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>4</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>309.000000:368.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>applicationBundleID</key>
        <string>com.apple.finder</string>
        <key>applicationBundleIDsByPath</key>
        <dict>
            <key>/System/Library/CoreServices/Finder.app</key>
            <string>com.apple.finder</string>
        </dict>
        <key>applicationPath</key>
        <string>/System/Library/CoreServices/Finder.app</string>
        <key>applicationPaths</key>
        <array>
            <string>/System/Library/CoreServices/Finder.app</string>
        </array>
        <key>inputTypeIdentifiers</key>
        <array>
            <string>public.audio</string>
            <string>public.movie</string>
        </array>
        <key>serviceApplicationBundleID</key>
        <string>com.apple.finder</string>
        <key>serviceApplicationPath</key>
        <string>/System/Library/CoreServices/Finder.app</string>
        <key>serviceInputTypeIdentifiers</key>
        <array>
            <string>public.audio</string>
            <string>public.movie</string>
        </array>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.servicesMenu</string>
    </dict>
</dict>
</plist>
EOF

# Create uninstall script
cat > "${SCRIPT_DIR}/uninstall_right_click_menu_macos.sh" << EOF
#!/bin/bash

echo "Removing DaVinci Resolve Subtitle Generator context menu for macOS..."

# Get directory of the workflow
WORKFLOW_DIR="\${HOME}/Library/Services/Generate Subtitles.workflow"

# Check if the service exists
if [ -d "\$WORKFLOW_DIR" ]; then
    echo "Removing service from \$WORKFLOW_DIR..."
    rm -rf "\$WORKFLOW_DIR"
    echo "Service removed successfully."
else
    echo "Service not found. Nothing to remove."
fi

echo "Done. You may need to restart Finder for the changes to take effect."
EOF

# Make the uninstall script executable
chmod +x "${SCRIPT_DIR}/uninstall_right_click_menu_macos.sh"

echo "Installation complete!"
echo
echo "You can now right-click on audio and video files in Finder and select:"
echo "    Services > Generate Subtitles with DaVinci Resolve"
echo
echo "To remove the service, run the uninstall_right_click_menu_macos.sh script."
echo
echo "Note: You may need to restart Finder for the changes to take effect."
echo "To restart Finder, hold Option+Right-click on the Finder icon in the Dock and select 'Relaunch'."

# Make the script executable
chmod +x "$WORKFLOW_DIR"

exit 0 