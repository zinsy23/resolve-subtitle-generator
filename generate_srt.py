#!/usr/bin/env python
import sys
import os
import glob
import time
import ctypes
from ctypes import wintypes
import logging
import argparse
import json
import tempfile
import subprocess
from pydub import AudioSegment
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)

def validate_resolve_paths():
    """Validate Resolve paths and prompt for custom paths if needed."""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resolve_paths.json")
    config = {}
    modified = False
    
    # Load saved paths if available
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                logging.info("Loaded custom paths from config file")
        except Exception as e:
            logging.warning(f"Failed to load config file: {str(e)}")
    
    # Get default API path based on OS
    if sys.platform.startswith("win"):  # Windows
        default_api_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
    elif sys.platform == "darwin":  # macOS
        default_api_path = r"/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    elif sys.platform.startswith("linux"):  # Linux
        default_api_path = r"/opt/resolve/Developer/Scripting"
    else:
        default_api_path = ""
    
    # Get default LIB path based on OS
    if sys.platform.startswith("win"):  # Windows
        default_lib_path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
    elif sys.platform == "darwin":  # macOS
        default_lib_path = r"/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif sys.platform.startswith("linux"):  # Linux
        default_lib_path = r"/opt/resolve/libs/Fusion/fusionscript.so"
    else:
        default_lib_path = ""
    
    # First check if default paths exist
    default_api_valid = os.path.isdir(default_api_path)
    default_lib_valid = os.path.isfile(default_lib_path)
    
    # Set API path
    if "RESOLVE_SCRIPT_API" in config:
        # Use custom path from config
        os.environ["RESOLVE_SCRIPT_API"] = config["RESOLVE_SCRIPT_API"]
    elif not os.getenv("RESOLVE_SCRIPT_API"):
        # Use default path
        os.environ["RESOLVE_SCRIPT_API"] = default_api_path
    
    # Check if API path exists
    api_path = os.environ.get("RESOLVE_SCRIPT_API", "")
    if not os.path.isdir(api_path):
        # Path doesn't exist, check if default path exists
        if default_api_valid:
            print(f"\nCustom DaVinci Resolve API path not found: {api_path}")
            print(f"Default path exists: {default_api_path}")
            use_default = input(f"Press Enter to use default path, or type a custom path: ")
            if not use_default.strip():
                os.environ["RESOLVE_SCRIPT_API"] = default_api_path
                if "RESOLVE_SCRIPT_API" in config:
                    del config["RESOLVE_SCRIPT_API"]  # Remove custom path from config
                    modified = True
            else:
                custom_path = use_default
                if os.path.isdir(custom_path):
                    os.environ["RESOLVE_SCRIPT_API"] = custom_path
                    config["RESOLVE_SCRIPT_API"] = custom_path
                    modified = True
                else:
                    print(f"Warning: Path '{custom_path}' does not exist, using default path")
                    os.environ["RESOLVE_SCRIPT_API"] = default_api_path
                    if "RESOLVE_SCRIPT_API" in config:
                        del config["RESOLVE_SCRIPT_API"]
                        modified = True
        else:
            print(f"\nDaVinci Resolve API path not found: {api_path}")
            print("Default path also not found. Please provide a valid path.")
            custom_path = input(f"Enter path to DaVinci Resolve Scripting folder: ")
            if os.path.isdir(custom_path):
                os.environ["RESOLVE_SCRIPT_API"] = custom_path
                config["RESOLVE_SCRIPT_API"] = custom_path
                modified = True
            else:
                print(f"Warning: Path '{custom_path}' does not exist, using default path anyway")
    
    # Set LIB path
    if "RESOLVE_SCRIPT_LIB" in config:
        # Use custom path from config
        os.environ["RESOLVE_SCRIPT_LIB"] = config["RESOLVE_SCRIPT_LIB"]
    elif not os.getenv("RESOLVE_SCRIPT_LIB"):
        # Use default path
        os.environ["RESOLVE_SCRIPT_LIB"] = default_lib_path
    
    # Check if LIB path exists
    lib_path = os.environ.get("RESOLVE_SCRIPT_LIB", "")
    if not os.path.isfile(lib_path):
        # Path doesn't exist, check if default path exists
        if default_lib_valid:
            print(f"\nCustom DaVinci Resolve Library not found: {lib_path}")
            print(f"Default path exists: {default_lib_path}")
            use_default = input(f"Press Enter to use default path, or type a custom path: ")
            if not use_default.strip():
                os.environ["RESOLVE_SCRIPT_LIB"] = default_lib_path
                if "RESOLVE_SCRIPT_LIB" in config:
                    del config["RESOLVE_SCRIPT_LIB"]  # Remove custom path from config
                    modified = True
            else:
                custom_path = use_default
                if os.path.isfile(custom_path):
                    os.environ["RESOLVE_SCRIPT_LIB"] = custom_path
                    config["RESOLVE_SCRIPT_LIB"] = custom_path
                    modified = True
                else:
                    print(f"Warning: File '{custom_path}' does not exist, using default path")
                    os.environ["RESOLVE_SCRIPT_LIB"] = default_lib_path
                    if "RESOLVE_SCRIPT_LIB" in config:
                        del config["RESOLVE_SCRIPT_LIB"]
                        modified = True
        else:
            print(f"\nDaVinci Resolve Library not found: {lib_path}")
            print("Default path also not found. Please provide a valid path.")
            custom_path = input(f"Enter path to DaVinci Resolve fusionscript library: ")
            if os.path.isfile(custom_path):
                os.environ["RESOLVE_SCRIPT_LIB"] = custom_path
                config["RESOLVE_SCRIPT_LIB"] = custom_path
                modified = True
            else:
                print(f"Warning: File '{custom_path}' does not exist, using default path anyway")
    
    # Save config if we have custom paths
    if modified:
        try:
            # If config is empty, delete the file instead
            if not config:
                if os.path.exists(config_file):
                    os.remove(config_file)
                    logging.info(f"Removed empty config file: {config_file}")
            else:
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                logging.info(f"Saved custom paths to {config_file}")
        except Exception as e:
            logging.warning(f"Failed to save config file: {str(e)}")

    logging.info(f"Using RESOLVE_SCRIPT_API: {os.environ.get('RESOLVE_SCRIPT_API')}")
    logging.info(f"Using RESOLVE_SCRIPT_LIB: {os.environ.get('RESOLVE_SCRIPT_LIB')}")

def test_resolve_import_in_subprocess():
    """Test importing DaVinciResolveScript in a separate process for safety"""
    logging.info("Testing DaVinci Resolve import in a separate process...")
    
    # Create a temporary Python file with the import test
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        test_script = f.name
        
        # Write a script that attempts the import and exits with code 0 if successful
        f.write(f'''
import os
import sys

# Set required environment variables
os.environ["RESOLVE_SCRIPT_API"] = r"{os.environ.get('RESOLVE_SCRIPT_API')}"
os.environ["RESOLVE_SCRIPT_LIB"] = r"{os.environ.get('RESOLVE_SCRIPT_LIB')}"

# Add module path to sys.path
resolve_script_path = os.path.join(os.environ.get('RESOLVE_SCRIPT_API', ''), 'Modules')
if os.path.exists(resolve_script_path) and resolve_script_path not in sys.path:
    sys.path.append(resolve_script_path)
    print(f"Added {{resolve_script_path}} to Python path")

# Try to import the module
try:
    import DaVinciResolveScript
    print("Successfully imported DaVinciResolveScript in test process")
    sys.exit(0)  # Success
except Exception as e:
    print(f"Error importing DaVinciResolveScript in test process: {{e}}")
    sys.exit(1)  # Failure
''')
    
    try:
        # Run the test script in a separate process
        logging.info(f"Running import test script: {test_script}")
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True, 
            text=True,
            timeout=10  # Set a timeout to avoid hanging
        )
        
        # Check the result
        if result.returncode == 0:
            logging.info("Import test succeeded in subprocess")
            logging.info(f"Subprocess stdout: {result.stdout}")
            return True
        else:
            logging.error(f"Import test failed in subprocess with exit code {result.returncode}")
            logging.error(f"Subprocess stderr: {result.stderr}")
            logging.error(f"Subprocess stdout: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("Import test timed out - this suggests the import would hang or crash")
        return False
    except Exception as e:
        logging.error(f"Error running import test: {e}")
        return False
    finally:
        # Clean up the temporary file
        try:
            os.unlink(test_script)
        except:
            pass

# Validate and set up Resolve paths
validate_resolve_paths()

# Add Resolve scripting module path
resolve_script_path = os.path.join(os.environ.get('RESOLVE_SCRIPT_API', ''), 'Modules')
if resolve_script_path not in sys.path and os.path.exists(resolve_script_path):
    sys.path.append(resolve_script_path)
    logging.info(f"Added {resolve_script_path} to Python path")

# First test the import in a subprocess for safety
if not test_resolve_import_in_subprocess():
    print("\nWARNING: DaVinci Resolve API import test failed in a separate process.")
    print("This may indicate compatibility issues with your Python environment and DaVinci Resolve.")
    print("The script will still attempt to continue, but may fail or crash.")
    
    should_continue = input("\nDo you want to continue anyway? (y/n): ")
    if should_continue.lower() != 'y':
        print("Exiting as requested.")
        sys.exit(1)

# Import DaVinci Resolve Script
try:
    import DaVinciResolveScript as dvr_script
    logging.info("Successfully imported DaVinciResolveScript")
except ImportError as e:
    logging.error(f"Failed to import DaVinciResolveScript: {str(e)}")
    print("\nError importing DaVinci Resolve script libraries. Please check:")
    print("1. DaVinci Resolve is properly installed")
    print("2. You have the correct version of Python (64-bit)")
    print("3. The paths to DaVinci Resolve libraries are correct")
    print("\nPaths checked:")
    print(f"API path: {os.environ.get('RESOLVE_SCRIPT_API', 'Not set')}")
    print(f"Library path: {os.environ.get('RESOLVE_SCRIPT_LIB', 'Not set')}")
    sys.exit(1)

def get_resolve():
    """Get the resolve object and ensure it's ready for use."""
    logging.info("Getting Resolve object...")
    
    # Import the module
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            raise Exception("Failed to get Resolve object")
        
        # Verify Resolve is responsive
        project_manager = resolve.GetProjectManager()
        if not project_manager:
            raise Exception("Failed to get project manager - Resolve may not be ready")
            
        # Switch to Edit page
        current_page = resolve.GetCurrentPage()
        if current_page != "edit":
            resolve.OpenPage("edit")
            time.sleep(1)  # Brief wait for page switch
            
        return resolve
    except Exception as e:
        logging.error(f"Error getting Resolve object: {str(e)}")
        raise

def is_resolve_running():
    """Check if DaVinci Resolve is running"""
    try:
        # Windows-specific process enumeration
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        titles = []
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        return any('DaVinci Resolve' in title for title in titles)
    except:
        # If we can't check, assume it's running
        return True

def check_resolve_installation():
    """Check if DaVinci Resolve is installed"""
    program_files = os.environ.get('PROGRAMFILES', '')
    resolve_path = os.path.join(program_files, 'Blackmagic Design', 'DaVinci Resolve', 'Resolve.exe')
    return os.path.exists(resolve_path)

def setup_resolve_env():
    """Set up environment variables for Resolve scripting"""
    # Check if Resolve is installed
    if not check_resolve_installation():
        print("ERROR: DaVinci Resolve is not installed in the expected location.")
        print("Please install DaVinci Resolve and try again.")
        sys.exit(1)

    # Check if Resolve is running
    if not is_resolve_running():
        print("ERROR: DaVinci Resolve is not running.")
        print("Please start DaVinci Resolve and try again.")
        sys.exit(1)

    program_data = os.environ.get('PROGRAMDATA', '')
    program_files = os.environ.get('PROGRAMFILES', '')
    
    # Set up environment variables as per documentation
    resolve_script_api = os.path.join(program_data, 
                                    'Blackmagic Design',
                                    'DaVinci Resolve',
                                    'Support',
                                    'Developer',
                                    'Scripting')
    
    resolve_script_lib = os.path.join(program_files,
                                    'Blackmagic Design',
                                    'DaVinci Resolve',
                                    'fusionscript.dll')

    # Verify paths exist
    if not os.path.exists(resolve_script_api):
        print(f"ERROR: Resolve Script API path not found: {resolve_script_api}")
        print("Please make sure DaVinci Resolve is properly installed.")
        sys.exit(1)

    if not os.path.exists(resolve_script_lib):
        print(f"ERROR: Resolve Script Library not found: {resolve_script_lib}")
        print("Please make sure DaVinci Resolve is properly installed.")
        sys.exit(1)
    
    os.environ['RESOLVE_SCRIPT_API'] = resolve_script_api
    os.environ['RESOLVE_SCRIPT_LIB'] = resolve_script_lib
    
    # Add to Python path
    if resolve_script_api not in sys.path:
        sys.path.append(resolve_script_api)
        modules_path = os.path.join(resolve_script_api, 'Modules')
        if os.path.exists(modules_path):
            sys.path.append(modules_path)

    print("\nEnvironment Setup:")
    print(f"RESOLVE_SCRIPT_API: {os.environ['RESOLVE_SCRIPT_API']}")
    print(f"RESOLVE_SCRIPT_LIB: {os.environ['RESOLVE_SCRIPT_LIB']}")
    print(f"Python Path: {sys.path}\n")

def import_resolve_script():
    """Import the DaVinciResolveScript module"""
    try:
        import DaVinciResolveScript as dvr_script
        return dvr_script
    except ImportError as e:
        print("\nERROR: Failed to import DaVinciResolveScript module")
        print(f"Error details: {str(e)}")
        print("\nPlease check:")
        print("1. DaVinci Resolve is properly installed")
        print("2. You have the correct version of Python (64-bit)")
        print("3. The environment variables are set correctly")
        print("\nPaths checked:")
        print(f"API path: {os.environ.get('RESOLVE_SCRIPT_API', 'Not set')}")
        print(f"Library path: {os.environ.get('RESOLVE_SCRIPT_LIB', 'Not set')}")
        sys.exit(1)

def expand_file_args(args):
    """Expand wildcards in file arguments"""
    expanded_files = []
    for arg in args:
        if '*' in arg or '?' in arg:
            expanded_files.extend(glob.glob(arg))
        else:
            expanded_files.append(arg)
    return expanded_files

def get_audio_duration(audio_file):
    """Get the duration of an audio file in seconds."""
    try:
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        logging.error(f"Error getting audio duration: {str(e)}")
        return 180  # Default to 3 minutes if we can't get duration

def wait_for_subtitles(timeline, max_attempts=30):
    """Wait for subtitle generation with increased timeout."""
    wait_time = 2  # Wait time in seconds between checks
    
    logging.info(f"Waiting for subtitle generation (max {max_attempts} attempts)...")
    
    for attempt in range(max_attempts):
        try:
            # First check if timeline is still valid
            if not timeline:
                logging.error("Timeline is None")
                return False
                
            # Try to get subtitle items using GetItemListInTrack instead of GetSubtitleItems
            items = timeline.GetItemListInTrack("subtitle", 1)
            if items and len(items) > 0:
                logging.info(f"Found {len(items)} subtitle items")
                return True
                
            logging.info(f"Attempt {attempt + 1}/{max_attempts}: No subtitles yet, waiting {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            logging.error(f"Error checking for subtitle items: {str(e)}")
            time.sleep(wait_time)
            continue
    
    logging.error("Timeout waiting for subtitles to appear")
    return False

def verify_subtitle_generation(timeline):
    """Verify that subtitles were generated successfully."""
    try:
        subtitle_items = timeline.GetSubtitleItems()
        if not subtitle_items:
            logging.error("No subtitle items found")
            return False
            
        logging.info(f"Found {len(subtitle_items)} subtitle items")
        
        # Check if any subtitles have content
        for item in subtitle_items:
            text = item.GetText()
            if text and text.strip():
                logging.info("Found subtitle with content")
                return True
                
        logging.error("No subtitles with content found")
        return False
    except Exception as e:
        logging.error(f"Error verifying subtitle generation: {str(e)}")
        return False

def create_project(resolve, project_name):
    """Create a new project with the given name."""
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        raise Exception("Failed to get Project Manager")
    
    # Check if project exists
    project = project_manager.GetProject(project_name)
    if project:
        logging.info(f"Using existing project: {project_name}")
        return project
    
    # Create new project if it doesn't exist
    logging.info(f"Creating new project: {project_name}")
    project = project_manager.CreateProject(project_name)
    if not project:
        raise Exception(f"Failed to create project: {project_name}")
    
    # Wait for project to be ready
    time.sleep(2)
    return project

def setup_timeline_tracks(timeline):
    """Set up timeline tracks for audio and subtitles."""
    logging.info("Setting up timeline tracks...")
    
    try:
        # Check current track count
        audio_tracks = timeline.GetTrackCount("audio")
        logging.info(f"Current audio track count: {audio_tracks}")
        
        # Add audio track if none exist
        if audio_tracks == 0:
            logging.info("No audio tracks found, adding one...")
            if not timeline.AddTrack("audio"):
                logging.error("Failed to add audio track")
                return False
            time.sleep(1)  # Wait for track creation
            
            # Verify audio track was created
            audio_tracks = timeline.GetTrackCount("audio")
            logging.info(f"Audio track count after creation: {audio_tracks}")
            if audio_tracks < 1:
                logging.error("No audio tracks found after creation")
                return False
        
        # Check subtitle tracks
        subtitle_tracks = timeline.GetTrackCount("subtitle")
        logging.info(f"Current subtitle track count: {subtitle_tracks}")
        
        # Add subtitle track if none exist
        if subtitle_tracks == 0:
            logging.info("No subtitle tracks found, adding one...")
            if not timeline.AddTrack("subtitle"):
                logging.error("Failed to add subtitle track")
                return False
            time.sleep(1)  # Wait for track creation
            
            # Verify subtitle track was created
            subtitle_tracks = timeline.GetTrackCount("subtitle")
            logging.info(f"Subtitle track count after creation: {subtitle_tracks}")
            if subtitle_tracks < 1:
                logging.error("No subtitle tracks found after creation")
                return False
        
        logging.info("Successfully set up timeline tracks")
        return True
    except Exception as e:
        logging.error(f"Error setting up timeline tracks: {str(e)}")
        return False

def create_subtitle_track(timeline, max_retries=3):
    """Create a subtitle track with retries."""
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to create subtitle track...")
            result = timeline.AddSubtitleTrack()
            if result:
                logging.info("Successfully created subtitle track")
                return True
            logging.error("AddSubtitleTrack returned False")
        except Exception as e:
            logging.error(f"Error creating subtitle track: {str(e)}")
        time.sleep(2)  # Wait before retrying
    return False

def setup_subtitle_track(timeline):
    """Set up subtitle track for the timeline."""
    logging.info("Setting up subtitle track...")
    
    try:
        # Check current subtitle tracks
        subtitle_tracks = timeline.GetSubtitleTrackCount()
        logging.info(f"Current subtitle track count: {subtitle_tracks}")
        
        # Add subtitle track if none exist
        if subtitle_tracks == 0:
            logging.info("No subtitle tracks found, adding one...")
            if not create_subtitle_track(timeline):
                logging.error("Failed to create subtitle track")
                return False
        
        # Get the subtitle track
        subtitle_track = timeline.GetSubtitleTrack(1)
        if not subtitle_track:
            logging.error("Failed to get subtitle track")
            return False
            
        logging.info("Successfully set up subtitle track")
        return True
    except Exception as e:
        logging.error(f"Error setting up subtitle track: {str(e)}")
        return False

def add_media_to_timeline(timeline, media_item):
    """Add media to timeline using alternative methods."""
    logging.info("Attempting to add media to timeline...")
    
    try:
        # Verify timeline is valid
        if not timeline or not hasattr(timeline, 'AppendToTimeline'):
            logging.error("Invalid timeline object")
            return False
        
        # Try to add media using different methods
        methods = [
            ("AppendToTimeline with list", lambda: timeline.AppendToTimeline([{"mediaPoolItem": media_item}])),
            ("AppendToTimeline without list", lambda: timeline.AppendToTimeline({"mediaPoolItem": media_item})),
            ("MediaPool AppendToTimeline", lambda: timeline.GetMediaPool().AppendToTimeline(media_item))
        ]
        
        for method_name, method_func in methods:
            try:
                logging.info(f"Trying {method_name}...")
                if method_func():
                    logging.info(f"{method_name} successful")
                    return True
            except Exception as e:
                logging.error(f"Error with {method_name}: {str(e)}")
                continue
        
        logging.error("All methods failed to add media to timeline")
        return False
    except Exception as e:
        logging.error(f"Error in add_media_to_timeline: {str(e)}")
        return False

def import_media_with_timeout(media_pool, file_path, timeout=30):
    """Import media with a timeout."""
    import threading
    import queue

    result_queue = queue.Queue()
    
    def import_worker():
        try:
            media_items = media_pool.ImportMedia([file_path])
            result_queue.put(("success", media_items))
        except Exception as e:
            result_queue.put(("error", str(e)))
    
    thread = threading.Thread(target=import_worker)
    thread.daemon = True
    thread.start()
    
    try:
        status, result = result_queue.get(timeout=timeout)
        if status == "error":
            raise Exception(f"Import failed: {result}")
        return result
    except queue.Empty:
        raise Exception(f"Import timed out after {timeout} seconds")
    finally:
        thread = None

def verify_media_import(media_pool, media_items, file_path):
    """Verify that media was imported correctly."""
    if not media_items:
        return False
        
    # Get the media item
    media_item = media_items[0] if isinstance(media_items, list) else media_items
    
    # Check if the media item exists in the media pool
    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        return False
        
    # Get all clips in the root folder
    clips = root_folder.GetClipList()
    if not clips:
        return False
        
    # Check if our media item is in the clips
    for clip in clips:
        if clip.GetName() == media_item.GetName():
            return True
            
    return False

def verify_timeline_media(timeline):
    """Verify that media was added to timeline correctly."""
    if not timeline:
        logging.error("Timeline is None")
        return False
        
    # Get timeline properties
    duration = timeline.GetEndFrame() - timeline.GetStartFrame()
    track_count = timeline.GetTrackCount("audio")
    logging.info(f"Timeline duration: {duration} frames")
    logging.info(f"Audio track count: {track_count}")
    
    # Check if timeline has any items
    items = timeline.GetItemListInTrack("audio", 1)
    if not items:
        logging.error("No items found in audio track 1")
        return False
        
    logging.info(f"Found {len(items)} items in audio track 1")
    for item in items:
        start = item.GetStart()
        end = item.GetEnd()
        name = item.GetName()
        logging.info(f"Audio item: {name}, Start: {start}, End: {end}")
    
    return True

def import_audio_file(media_pool, root_folder, audio_file):
    """Import an audio file into the media pool."""
    try:
        # Get absolute path and normalize it
        abs_audio_path = os.path.abspath(audio_file)
        abs_audio_path = os.path.normpath(abs_audio_path)
        logging.info(f"Attempting to import from path: {abs_audio_path}")
        
        # Import the media
        media_items = media_pool.ImportMedia([abs_audio_path])
        if not media_items:
            logging.error("Failed to import media")
            return False
            
        # Verify the media import
        if not verify_media_import(media_pool, media_items, abs_audio_path):
            logging.error("Media import verification failed")
            return False
            
        logging.info("Successfully imported and verified audio file")
        return True
    except Exception as e:
        logging.error(f"Error importing audio file: {str(e)}")
        return False

def create_timeline_with_media(project, media_pool, timeline_name):
    """Create a timeline with media from the media pool."""
    try:
        # Get the most recently imported clip
        root_folder = media_pool.GetRootFolder()
        if not root_folder:
            logging.error("Failed to get root folder")
            return None
            
        clips = root_folder.GetClipList()
        if not clips:
            logging.error("No clips found in media pool")
            return None
            
        # Use the most recent clip
        media_item = clips[-1]
        
        # Create timeline with media
        logging.info(f"Creating timeline '{timeline_name}' with media...")
        timeline = media_pool.CreateTimelineFromClips(timeline_name, [media_item])
        if not timeline:
            logging.error("Failed to create timeline with media")
            return None
            
        # Set as current timeline
        project.SetCurrentTimeline(timeline)
        time.sleep(2)  # Wait for timeline to become current
        
        # Verify timeline was created with media
        current_timeline = project.GetCurrentTimeline()
        if not current_timeline or current_timeline.GetName() != timeline_name:
            logging.error("Failed to set timeline as current")
            return None
            
        # Verify media was added
        items = current_timeline.GetItemListInTrack("audio", 1)
        if not items:
            logging.error("No media found in timeline")
            return None
            
        logging.info("Successfully created timeline with media")
        return current_timeline
    except Exception as e:
        logging.error(f"Error creating timeline with media: {str(e)}")
        return None

def ensure_edit_page(resolve):
    """Ensure we're on the Edit page."""
    try:
        current_page = resolve.GetCurrentPage()
        if current_page != "edit":
            resolve.OpenPage("edit")
            time.sleep(1)  # Wait for page switch
        return True
    except Exception as e:
        logging.error(f"Error ensuring Edit page: {str(e)}")
        return False

def get_current_timeline(resolve):
    """Get the current timeline, ensuring we're on the Edit page first."""
    try:
        # Ensure we're on the Edit page
        if not ensure_edit_page(resolve):
            return None
            
        # Get project and timeline
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            return None
            
        timeline = project.GetCurrentTimeline()
        return timeline
    except Exception as e:
        logging.error(f"Error getting current timeline: {str(e)}")
        return None

def get_subtitle_items(timeline):
    """Get subtitle items from the timeline."""
    try:
        # Get subtitle track
        subtitle_track_count = timeline.GetTrackCount("subtitle")
        if subtitle_track_count < 1:
            logging.error("No subtitle tracks found")
            return None
            
        # Get items from first subtitle track
        items = timeline.GetItemListInTrack("subtitle", 1)
        if not items:
            logging.error("No items found in subtitle track")
            return None
            
        logging.info(f"Found {len(items)} items in subtitle track")
        
        # Extract text and timing from items
        subtitle_items = []
        for i, item in enumerate(items):
            text = item.GetName()
            logging.info(f"Raw text from Resolve (item {i}): {repr(text)}")  # Use repr to show special characters
            start = item.GetStart()
            end = item.GetEnd()
            subtitle_items.append({
                'text': text,
                'start': start,
                'end': end,
                'index': i + 1
            })
            logging.info(f"Found text in item {i}: {text}")
            
        return subtitle_items
    except Exception as e:
        logging.error(f"Error getting subtitle items: {str(e)}")
        return None

def format_timecode(frames):
    """Convert frames to SRT timecode format (assuming 24fps)."""
    total_seconds = frames / 24  # Convert frames to seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds * 1000) % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def write_srt_file(srt_path, subtitle_items):
    """Write subtitle items to an SRT file."""
    try:
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, item in enumerate(subtitle_items, 1):
                text = item['text']
                # Split on Resolve's line separator character (U+2028)
                lines = text.split('\u2028')
                # Format with line break and bold tags
                formatted_text = f"<b>{lines[0]}\n{lines[1]}</b>" if len(lines) > 1 else f"<b>{text}</b>"
                
                # Write the subtitle entry
                f.write(f"{i}\n")
                f.write(f"{format_timecode(item['start'])} --> {format_timecode(item['end'])}\n")
                f.write(formatted_text + "\n\n")
        
        logging.info(f"Successfully wrote SRT file to {srt_path}")
        return True
    except Exception as e:
        logging.error(f"Error writing SRT file: {str(e)}")
        return False

def create_subtitles_from_audio(timeline):
    """Create subtitles from audio in the timeline."""
    try:
        # Ensure we're on the Edit page
        if not ensure_edit_page(get_resolve()):
            return False
            
        # Get Resolve instance for constants
        resolve = get_resolve()
        
        # Set up auto caption settings with proper Resolve constants
        settings = {
            resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
            resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,
            resolve.SUBTITLE_CHARS_PER_LINE: 42,
            resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_DOUBLE,
            resolve.SUBTITLE_GAP: 0
        }
            
        # Create subtitles with specified settings
        if not timeline.CreateSubtitlesFromAudio(settings):
            logging.error("Failed to create subtitles from audio")
            return False
            
        logging.info("Successfully initiated subtitle creation")
        return True
    except Exception as e:
        logging.error(f"Error creating subtitles from audio: {str(e)}")
        return False

def get_current_project():
    """Get the current project in Resolve."""
    try:
        resolve = get_resolve()
        if not resolve:
            logging.error("Failed to get Resolve object")
            return None
            
        projectManager = resolve.GetProjectManager()
        if not projectManager:
            logging.error("Failed to get project manager")
            return None
            
        currentProject = projectManager.GetCurrentProject()
        if not currentProject:
            logging.error("No project is currently open")
            return None
            
        logging.info(f"Using current project: {currentProject.GetName()}")
        return currentProject
    except Exception as e:
        logging.error(f"Error getting current project: {str(e)}")
        return None

def generate_srt_for_file(audio_file):
    """Generate SRT file for a given audio file."""
    try:
        logging.info(f"Starting SRT generation for: {audio_file}")
        
        # Get output path
        output_path = os.path.splitext(audio_file)[0] + ".srt"
        logging.info(f"Output SRT will be saved to: {output_path}")
        
        # Get Resolve object
        logging.info("Getting Resolve object...")
        resolve = get_resolve()
        if not resolve:
            logging.error("Failed to get Resolve object")
            return False
            
        # Get current project
        logging.info("Getting current project...")
        project = get_current_project()
        if not project:
            logging.error("No project is open. Please open a project first.")
            return False
            
        # Get media pool
        logging.info("Getting media pool...")
        mediaPool = project.GetMediaPool()
        if not mediaPool:
            logging.error("Failed to get media pool")
            return False
            
        # Get root folder
        logging.info("Getting root folder...")
        rootFolder = mediaPool.GetRootFolder()
        if not rootFolder:
            logging.error("Failed to get root folder")
            return False
            
        # Import audio file
        logging.info("Importing audio file...")
        if not import_audio_file(mediaPool, rootFolder, audio_file):
            logging.error("Failed to import audio file")
            return False
            
        # Create timeline with media
        logging.info("Creating timeline with media...")
        timeline = create_timeline_with_media(project, mediaPool, os.path.basename(audio_file))
        if not timeline:
            logging.error("Failed to create timeline")
            return False
            
        # Verify project state
        logging.info("Verifying project state...")
        if not verify_project_state(project, timeline):
            logging.error("Project state verification failed")
            return False
            
        # Clear existing subtitle tracks
        logging.info("Clearing existing subtitle tracks...")
        if not clear_subtitle_tracks(timeline):
            logging.error("Failed to clear subtitle tracks")
            return False
            
        # Setup timeline tracks
        logging.info("Setting up timeline tracks...")
        if not setup_timeline_tracks(timeline):
            logging.error("Failed to setup timeline tracks")
            return False
            
        # Generate subtitles
        logging.info("Generating subtitles...")
        if not create_subtitles_from_audio(timeline):
            logging.error("Failed to generate subtitles")
            return False
            
        # Wait for subtitle generation
        logging.info("Waiting for subtitle generation (max 30 attempts)...")
        if not wait_for_subtitles(timeline):
            logging.error("Failed to generate subtitles")
            return False
            
        # Verify timeline is still valid
        if not verify_timeline(timeline):
            logging.error("Timeline is no longer valid after generating subtitles")
            return False
            
        # Get subtitle items
        subtitle_items = get_subtitle_items(timeline)
        if not subtitle_items:
            logging.error("Failed to get subtitle items")
            return False
            
        # Write SRT file
        logging.info(f"Writing SRT to: {output_path}")
        if not write_srt_file(output_path, subtitle_items):
            logging.error("Failed to write SRT file")
            return False
            
        logging.info(f"Successfully wrote SRT file to {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error in generate_srt_for_file: {str(e)}")
        return False

def verify_project_state(project, timeline):
    """Verify that the project and timeline are in a valid state."""
    try:
        # Check project is valid
        if not project:
            logging.error("Project is None")
            return False
            
        # Check timeline is valid
        if not timeline:
            logging.error("Timeline is None")
            return False
            
        # Check timeline is current
        current_timeline = project.GetCurrentTimeline()
        if not current_timeline or current_timeline.GetName() != timeline.GetName():
            logging.error("Timeline is not current")
            return False
            
        # Check timeline has media
        items = timeline.GetItemListInTrack("audio", 1)
        if not items:
            logging.error("No media in timeline")
            return False
            
        logging.info("Project state verification successful")
        return True
    except Exception as e:
        logging.error(f"Error verifying project state: {str(e)}")
        return False

def verify_timeline(timeline):
    """Verify that the timeline is valid and has required tracks."""
    try:
        if not timeline:
            logging.error("Timeline is None")
            return False
            
        # Check audio track exists
        audio_tracks = timeline.GetTrackCount("audio")
        if audio_tracks < 1:
            logging.error("No audio tracks found")
            return False
            
        # Check subtitle track exists
        subtitle_tracks = timeline.GetTrackCount("subtitle")
        if subtitle_tracks < 1:
            logging.error("No subtitle tracks found")
            return False
            
        logging.info("Timeline verification successful")
        return True
    except Exception as e:
        logging.error(f"Error verifying timeline: {str(e)}")
        return False

def clear_subtitle_tracks(timeline):
    """Clear all subtitle tracks in the timeline."""
    try:
        subtitle_track_count = timeline.GetTrackCount("subtitle")
        for track_index in range(1, subtitle_track_count + 1):
            items = timeline.GetItemListInTrack("subtitle", track_index)
            for item in items:
                timeline.DeleteItems([item])
        logging.info("Cleared all subtitle tracks")
        return True
    except Exception as e:
        logging.error(f"Error clearing subtitle tracks: {str(e)}")
        return False

def main():
    # Get files to process
    if len(sys.argv) > 1:
        # Process files provided as arguments
        files_to_process = []
        for arg in sys.argv[1:]:
            if '*' in arg or '?' in arg:
                # Expand wildcards
                files_to_process.extend(glob.glob(arg))
            else:
                files_to_process.append(arg)
    else:
        # Process all MP3 files in samples directory
        samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        files_to_process = [os.path.join(samples_dir, f) for f in os.listdir(samples_dir) if f.endswith('.MP3')]
    
    if not files_to_process:
        print("No files to process")
        return
    
    # Get initial Resolve setup
    try:
        resolve = get_resolve()
        if not resolve:
            print("Failed to get Resolve object")
            return
            
        project = get_current_project()
        if not project:
            print("No project is currently open. Please open a project first.")
            return
            
        media_pool = project.GetMediaPool()
        if not media_pool:
            print("Failed to get media pool")
            return
            
        root_folder = media_pool.GetRootFolder()
        if not root_folder:
            print("Failed to get root folder")
            return
    except Exception as e:
        print(f"Error setting up Resolve: {str(e)}")
        return
    
    # Process each file sequentially
    successful = 0
    for file_path in files_to_process:
        try:
            print(f"\nProcessing {os.path.basename(file_path)}...")
            
            # Generate SRT
            if generate_srt_for_file(file_path):
                successful += 1
                print(f"Successfully generated SRT for {os.path.basename(file_path)}")
            else:
                print(f"Failed to generate SRT for {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {str(e)}")
            continue
    
    print(f"\nProcessed {len(files_to_process)} file(s), {successful} successful")

if __name__ == "__main__":
    main() 