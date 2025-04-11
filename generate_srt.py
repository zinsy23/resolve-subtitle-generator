#!/usr/bin/env python
import sys
import os
import glob
import time
import ctypes
from ctypes import wintypes
import logging
import argparse
from pydub import AudioSegment
import DaVinciResolveScript as dvr_script
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set Resolve environment variables if not set
if not os.getenv("RESOLVE_SCRIPT_API"):
    os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
if not os.getenv("RESOLVE_SCRIPT_LIB"):
    os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"

# Add Resolve scripting module path
resolve_script_path = os.path.join(os.environ.get('RESOLVE_SCRIPT_API', ''), 'Modules')
if resolve_script_path not in sys.path and os.path.exists(resolve_script_path):
    sys.path.append(resolve_script_path)
    logging.info(f"Added {resolve_script_path} to Python path")

# Import DaVinci Resolve Script
try:
    import DaVinciResolveScript as dvr_script
    logging.info("Successfully imported DaVinciResolveScript")
except ImportError as e:
    logging.error(f"Failed to import DaVinciResolveScript: {str(e)}")
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

def create_timeline_with_media(project, media_pool, media_item, timeline_name):
    """Create a timeline with media using the media pool."""
    logging.info("Creating timeline with media...")
    
    try:
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
    """Get subtitle items and their text from the timeline"""
    try:
        subtitle_items = []
        
        # Try to get items in subtitle track
        try:
            items = timeline.GetItemListInTrack("subtitle", 1)
            if items:
                logging.info("Found %d items in subtitle track", len(items))
                for i, item in enumerate(items):
                    try:
                        # Try to get text using GetName
                        text = item.GetName()
                        if text:
                            logging.info("Found text in item %d: %s", i, text)
                            subtitle_items.append({
                                'index': i + 1,
                                'text': text,
                                'start': item.GetStart(),
                                'end': item.GetEnd()
                            })
                    except Exception as e:
                        logging.error("Error getting text from item %d: %s", i, str(e))
            else:
                logging.info("No items found in subtitle track")
        except Exception as e:
            logging.error("Error getting items from subtitle track: %s", str(e))
            
        return subtitle_items
    except Exception as e:
        logging.error("Error getting subtitle items: %s", str(e))
        return []

def convert_edl_to_srt(edl_path, srt_path, subtitle_items):
    """
    Convert EDL/CSV format to SRT format, using the actual subtitle text and timing from subtitle_items.
    """
    try:
        logging.info(f"Writing SRT to: {srt_path}")
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            for item in subtitle_items:
                # Get the text and timing for this subtitle
                text = item.get('text', '')
                start_frames = item.get('start', 0)
                end_frames = item.get('end', 0)
                
                if not text:
                    continue
                
                # Convert frames to timecode (assuming 24fps)
                def frames_to_srt_tc(frames):
                    total_seconds = frames / 24  # Convert frames to seconds
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    seconds = int(total_seconds % 60)
                    milliseconds = int((total_seconds * 1000) % 1000)
                    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
                
                start_srt = frames_to_srt_tc(start_frames)
                end_srt = frames_to_srt_tc(end_frames)
                
                # Write SRT entry
                srt_file.write(f"{item['index']}\n")
                srt_file.write(f"{start_srt} --> {end_srt}\n")
                srt_file.write(f"{text}\n\n")
                        
        logging.info("Successfully wrote SRT file")
        return True
    except Exception as e:
        logging.error(f"Error writing SRT file: {str(e)}")
        return False

def generate_srt_for_file(audio_file):
    """Generate SRT file for the given audio file."""
    try:
        # Get the base name without extension for the SRT file
        base_name = os.path.splitext(audio_file)[0]
        srt_path = f"{base_name}.srt"
        txt_path = f"{base_name}.txt"
        
        logging.info(f"Starting SRT generation for: {audio_file}")
        logging.info(f"Output SRT will be saved to: {srt_path}")
        
        # Get Resolve and ensure it's ready
        resolve = get_resolve()
        if not resolve:
            logging.error("Failed to get Resolve object")
            return False
            
        # Get project manager and create new project
        logging.info("Getting project manager...")
        project_manager = resolve.GetProjectManager()
        if not project_manager:
            raise Exception("Failed to get project manager")
        logging.info("Successfully got project manager")

        # Create new project
        project_name = f"SRT_{int(time.time())}"
        logging.info(f"Creating new project: {project_name}")
        project = project_manager.CreateProject(project_name)
        if not project:
            raise Exception("Failed to create project")
        time.sleep(2)  # Increased wait time for project creation
        logging.info("Successfully created project")

        # Get media pool
        logging.info("Getting media pool...")
        media_pool = project.GetMediaPool()
        if not media_pool:
            raise Exception("Failed to get media pool")
        logging.info("Successfully got media pool")

        # Get root folder
        logging.info("Getting root folder...")
        root_folder = media_pool.GetRootFolder()
        if not root_folder:
            raise Exception("Failed to get root folder")
        logging.info("Successfully got root folder")
        
        # Import audio file
        logging.info("Importing audio file...")
        try:
            # Get absolute path and normalize it
            abs_audio_path = os.path.abspath(audio_file)
            abs_audio_path = os.path.normpath(abs_audio_path)
            logging.info(f"Attempting to import from path: {abs_audio_path}")
            
            # Import the media with timeout
            media_items = import_media_with_timeout(media_pool, abs_audio_path)
            if not media_items:
                raise Exception("Failed to import media")
                
            # Verify the media import
            if not verify_media_import(media_pool, media_items, abs_audio_path):
                raise Exception("Media import verification failed")
            
            media_item = media_items[0] if isinstance(media_items, list) else media_items
            logging.info("Successfully imported and verified audio file")
            
            # Create timeline with media
            timeline_name = os.path.splitext(os.path.basename(audio_file))[0]
            timeline = create_timeline_with_media(project, media_pool, media_item, timeline_name)
            if not timeline:
                raise Exception("Failed to create timeline with media")
            
            # Verify project is valid
            logging.info("Verifying project state...")
            project_name = project.GetName()
            if not project_name:
                logging.error("Project is not valid")
                return False
            logging.info(f"Current project: {project_name}")
            
            # Ensure we're on the Edit page
            if not ensure_edit_page(resolve):
                logging.error("Failed to switch to Edit page")
                return False
            logging.info("Successfully switched to Edit page")
            
            # Get current timeline and verify
            timeline = get_current_timeline(resolve)
            if not timeline:
                logging.error("Timeline is not valid")
                return False
            timeline_name = timeline.GetName()
            logging.info(f"Current timeline: {timeline_name}")
            
            # Setup timeline tracks
            logging.info("Setting up timeline tracks...")
            if not setup_timeline_tracks(timeline):
                logging.error("Failed to setup timeline tracks")
                return False
            logging.info("Successfully set up timeline tracks")
            
            # Get timeline again to ensure it's still valid
            timeline = get_current_timeline(resolve)
            if not timeline:
                logging.error("Timeline became invalid after track setup")
                return False
            logging.info("Timeline is still valid after track setup")
            
            # Try to generate subtitles
            logging.info("Generating subtitles...")
            try:
                result = timeline.CreateSubtitlesFromAudio()
                if not result:
                    logging.error("Failed to generate subtitles")
                    return False
                logging.info("Successfully generated subtitles")
            except Exception as e:
                logging.error(f"Error during subtitle generation: {str(e)}")
                return False
            
            # Wait for subtitle generation
            if not wait_for_subtitles(timeline):
                logging.error("Failed waiting for subtitles")
                return False
            
            # Get timeline again to ensure it's still valid
            timeline = get_current_timeline(resolve)
            if not timeline:
                logging.error("Timeline became invalid after generating subtitles")
                return False
            logging.info("Timeline is still valid after generating subtitles")
            
            # Get subtitle items with timing information
            subtitle_items = get_subtitle_items(timeline)
            if not subtitle_items:
                logging.error("No subtitle items found")
                return False
            logging.info(f"Found {len(subtitle_items)} subtitle items")
            
            # Write SRT file directly using subtitle timing information
            if convert_edl_to_srt(txt_path, srt_path, subtitle_items):
                logging.info(f"Successfully wrote SRT file to {srt_path}")
                return True
            else:
                logging.error("Failed to write SRT file")
                return False
            
        except Exception as e:
            logging.error(f"Error during subtitle generation/export: {str(e)}")
            return False
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
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