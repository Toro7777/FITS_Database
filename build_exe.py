"""
Build script to create standalone FITS_Database.exe

This script uses PyInstaller to compile fits_gui_database.py into a standalone
executable that doesn't require Python or any dependencies to be installed.

Usage:
    python build_exe.py

Result:
    Creates: dist/FITS_Database.exe (~150-200 MB)
    
Requirements:
    pip install pyinstaller
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path
import shutil

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Clean up previous builds
    print("Cleaning up previous builds...")
    for folder in ['build', 'dist', '__pycache__']:
        path = script_dir / folder
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {folder}/")
    
    print("\n" + "="*60)
    print("Building FITS_Database.exe with PyInstaller...")
    print("="*60 + "\n")
    
    # PyInstaller build command
    build_args = [
        str(script_dir / 'fits_gui_database.py'),
        '--onefile',  # Single executable file (vs folder with dependencies)
        '--windowed',  # No console window
        '--name=FITS_Database',  # Output name
        '--icon=FITS_icon.ico' if (script_dir / 'FITS_icon.ico').exists() else '',  # Optional icon
        '--add-data=FITS_Viewer:FITS_Viewer',  # Include FITS_Viewer folder
        '--hidden-import=astropy',
        '--hidden-import=astropy.io.fits',
        '--hidden-import=pandas',
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
        '--distpath=' + str(script_dir / 'dist'),
        '--workpath=' + str(script_dir / 'build'),
        '--specpath=' + str(script_dir),
    ]
    
    # Remove empty strings from args
    build_args = [arg for arg in build_args if arg]
    
    try:
        PyInstaller.__main__.run(build_args)
        
        print("\n" + "="*60)
        print("✓ Build successful!")
        print("="*60)
        print(f"\nExecutable created at:")
        print(f"  {script_dir}/dist/FITS_Database.exe")
        print(f"\nFile size: ~150-200 MB")
        print(f"\nTo test the executable:")
        print(f"  .\\dist\\FITS_Database.exe")
        print(f"\nTo distribute, share the .exe file with colleagues.")
        print(f"They can run it directly without installing Python!")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        print("\nMake sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        return 1

if __name__ == '__main__':
    sys.exit(main())
