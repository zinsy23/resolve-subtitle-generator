"""
DaVinci Resolve scripting helper functions.
"""

import os
import sys

def get_resolve():
    """Get the DaVinci Resolve object."""
    try:
        # Check if the required environment variables are set
        script_api = os.environ.get('RESOLVE_SCRIPT_API')
        script_lib = os.environ.get('RESOLVE_SCRIPT_LIB')
        
        if not script_api or not script_lib:
            print("\nEnvironment variables not set correctly:")
            print(f"RESOLVE_SCRIPT_API: {script_api or 'Not set'}")
            print(f"RESOLVE_SCRIPT_LIB: {script_lib or 'Not set'}")
            return None
            
        # Check if the directories exist
        if not os.path.exists(script_api):
            print(f"\nRESOLVE_SCRIPT_API directory does not exist: {script_api}")
            return None
            
        if not os.path.exists(script_lib):
            print(f"\nRESOLVE_SCRIPT_LIB file does not exist: {script_lib}")
            return None
            
        # Check if the Modules directory exists
        modules_dir = os.path.join(script_api, 'Modules')
        if not os.path.exists(modules_dir):
            print(f"\nModules directory does not exist: {modules_dir}")
            return None
            
        # List contents of the Modules directory
        print("\nContents of Modules directory:")
        for item in os.listdir(modules_dir):
            print(f"- {item}")
            
        # Try to import DaVinciResolveScript
        try:
            import DaVinciResolveScript
            print("\nSuccessfully imported DaVinciResolveScript module")
            resolve = DaVinciResolveScript.scriptapp("Resolve")
            if resolve:
                print("\nSuccessfully connected to DaVinci Resolve")
                return resolve
            else:
                print("\nFailed to connect to DaVinci Resolve - is it running?")
                return None
        except ImportError as e:
            print(f"\nError importing DaVinciResolveScript: {str(e)}")
            print("\nPython path:")
            for path in sys.path:
                print(f"- {path}")
            return None
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return None

def create_project(resolve, project_name):
    """Create a new project with the given name."""
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        print("Error: Could not get Project Manager")
        return None
    
    # Close current project if any
    current_project = project_manager.GetCurrentProject()
    if current_project:
        project_manager.CloseProject(current_project)
    
    # Sanitize project name - remove special characters
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not safe_name:
        safe_name = "SRT_Generation"
    
    print(f"\nCreating project: {safe_name}")
    
    # Create new project
    project = project_manager.CreateProject(safe_name)
    if not project:
        print(f"Error: Could not create project {safe_name}")
        return None
    
    print("Project created successfully")
    return project

def create_timeline(project, timeline_name):
    """Create a new timeline with the given name."""
    if not project:
        print("Error: No project provided")
        return None
    
    # Create new timeline
    timeline = project.GetMediaPool().CreateEmptyTimeline(timeline_name)
    if not timeline:
        print(f"Error: Could not create timeline {timeline_name}")
        return None
    
    return timeline

def import_audio(project, timeline, audio_file):
    """Import an audio file into the timeline."""
    if not project or not timeline:
        print("Error: No project or timeline provided")
        return False
    
    media_pool = project.GetMediaPool()
    if not media_pool:
        print("Error: Could not get Media Pool")
        return False
    
    # Import audio file
    imported = media_pool.ImportMedia(audio_file)
    if not imported:
        print(f"Error: Could not import audio file {audio_file}")
        return False
    
    # Add to timeline
    media_pool.AppendToTimeline(imported)
    return True

def generate_subtitles(timeline):
    """Generate subtitles for the current timeline."""
    if not timeline:
        print("Error: No timeline provided")
        return False
    
    # Switch to Edit page
    resolve = get_resolve()
    if not resolve:
        return False
    
    resolve.OpenPage("edit")
    
    # Generate subtitles
    timeline.GenerateSubtitles()
    return True

def export_srt(timeline, output_path):
    """Export subtitles as SRT file."""
    if not timeline:
        print("Error: No timeline provided")
        return False
    
    # Export SRT
    success = timeline.ExportSubtitles(output_path, "srt")
    if not success:
        print(f"Error: Could not export SRT to {output_path}")
        return False
    
    return True 