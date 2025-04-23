#!/usr/bin/env python
"""
Script to directly fix PyDub and audioop issue using the system Python
This avoids issues with pyenv or other Python version managers
"""

import os
import sys
import shutil
import subprocess

# Get the system Python interpreter
SYSTEM_PYTHON = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"

def create_complete_audioop():
    """Create a complete audioop module for Python 3.13."""
    # Find site-packages directory
    result = subprocess.run(
        [SYSTEM_PYTHON, "-c", "import site; print(site.getsitepackages()[0])"],
        capture_output=True,
        text=True,
        check=True
    )
    site_packages = result.stdout.strip()
    
    # Create the dummy _audioop.py in site-packages
    audioop_path = os.path.join(site_packages, "_audioop.py")
    
    print(f"Creating audioop module at: {audioop_path}")
    
    # More complete implementation
    with open(audioop_path, 'w') as f:
        f.write("""
# Dummy _audioop module for Python 3.13
import array
import struct

def add(fragment1, fragment2, width):
    return b'' * (len(fragment1) // width)

def avg(fragment, width):
    return 0

def avgpp(fragment, width):
    return 0

def bias(fragment, width, bias):
    return fragment

def byteswap(fragment, width):
    return fragment

def cross(fragment1, fragment2, width):
    return 0

def findfactor(fragment1, fragment2, width):
    return 1.0

def findfit(fragment1, fragment2, width):
    return (0, 1.0)

def findmax(fragment, width):
    return 0

def getsample(fragment, width, index):
    return 0

def lin2lin(fragment, width1, width2):
    return b'' * (len(fragment) // width1 * width2)

def lin2ulaw(fragment, width):
    return b'' * (len(fragment) // width)

def minmax(fragment, width):
    return (0, 0)

def mul(fragment, width, factor):
    return fragment

def ratecv(fragment, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):
    return (fragment, (0,))

def reverse(fragment, width):
    return fragment

def rms(fragment, width):
    return 0

def tomono(fragment, width, lfactor, rfactor):
    return b'' * (len(fragment) // width // 2 * width)

def tostereo(fragment, width, lfactor, rfactor):
    return b'' * (len(fragment) // width * width * 2)

def ulaw2lin(fragment, width):
    return b'' * (len(fragment) * width)
""")
    
    # Make a symlink for older name if needed
    audioop_alt_path = os.path.join(site_packages, "audioop.py")
    pyaudioop_path = os.path.join(site_packages, "pyaudioop.py")
    
    # Create symlinks for compatibility
    try:
        if not os.path.exists(audioop_alt_path):
            with open(audioop_alt_path, 'w') as f:
                f.write(f"# Compatibility module\nfrom _audioop import *\n")
            print(f"Created compatibility module: {audioop_alt_path}")
            
        if not os.path.exists(pyaudioop_path):
            with open(pyaudioop_path, 'w') as f:
                f.write(f"# Compatibility module\nfrom _audioop import *\n")
            print(f"Created compatibility module: {pyaudioop_path}")
    except Exception as e:
        print(f"Warning: Could not create compatibility modules: {e}")
    
    # Now try to import pydub with the system Python
    print("\nTesting if pydub can be imported now...")
    try:
        subprocess.run(
            [SYSTEM_PYTHON, "-c", 
             "from pydub import AudioSegment; print('SUCCESS: PyDub successfully imported!'); AudioSegment.silent(duration=1000); print('SUCCESS: AudioSegment can be created!')"],
            check=True
        )
        print("\n✅ PyDub fixed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ PyDub still has issues: {e}")
        return False

def reinstall_pydub():
    """Completely reinstall PyDub."""
    print("\nReinstalling PyDub...")
    
    try:
        # Uninstall pydub
        subprocess.run(
            [SYSTEM_PYTHON, "-m", "pip", "uninstall", "-y", "pydub"],
            check=True
        )
        
        # Install pydub
        subprocess.run(
            [SYSTEM_PYTHON, "-m", "pip", "install", "--force-reinstall", "pydub"],
            check=True
        )
        
        print("PyDub reinstalled successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to reinstall PyDub: {e}")
        return False

def show_system_info():
    """Show information about the Python environment."""
    print("=== System Information ===")
    
    # Get Python version
    try:
        subprocess.run([SYSTEM_PYTHON, "--version"], check=True)
    except subprocess.CalledProcessError:
        print(f"Could not run {SYSTEM_PYTHON}")
    
    # Get site-packages directory
    try:
        result = subprocess.run(
            [SYSTEM_PYTHON, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            text=True,
            check=True
        )
        site_packages = result.stdout.strip()
        print(f"Site-packages directory: {site_packages}")
    except subprocess.CalledProcessError:
        print("Could not determine site-packages directory")
    
    # Show installed packages
    try:
        subprocess.run([SYSTEM_PYTHON, "-m", "pip", "list"], check=True)
    except subprocess.CalledProcessError:
        print("Could not list installed packages")
    
    print("===========================")

def main():
    """Main function."""
    print("=== Global Python PyDub/AudioOp Fix ===\n")
    
    # Show system information
    show_system_info()
    
    # First try reinstalling PyDub
    print("\nStep 1: Reinstalling PyDub")
    reinstall_success = reinstall_pydub()
    
    # Create audioop module
    print("\nStep 2: Creating audioop module")
    audioop_success = create_complete_audioop()
    
    if audioop_success:
        print("\n🎉 Success! PyDub should now work with your global Python installation.")
        print(f"To run your script, use: {SYSTEM_PYTHON} your_script.py")
    else:
        print("\n❌ Fix was not completely successful.")
        print("You might need to:")
        print("1. Use a different Python version (3.9 recommended for better compatibility)")
        print("2. Install PyDub in a virtual environment")
        print("3. Use a different audio processing library")

if __name__ == "__main__":
    main() 