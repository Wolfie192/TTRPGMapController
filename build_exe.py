import PyInstaller.__main__
import os

def build():
    # Define the entry point
    entry_point = 'main.py'
    
    # PyInstaller arguments
    args = [
        entry_point,
        '--onefile',            # Bundle into a single executable
        '--noconsole',          # Don't open a command prompt window
        '--name=TTRPG_MapTool', # Name of the output .exe
        '--clean',              # Clean cache before building
        # If you have an icon, uncomment the line below:
        # '--icon=assets/icon.ico', 
    ]

    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()