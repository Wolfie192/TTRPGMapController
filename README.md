# TTRPG Map Controller

A desktop map viewer for tabletop role-playing games. Load a map on the control screen, then pan, zoom, or rotate it while a second player screen mirrors the view. The player screen can be moved to a second display and shown full-screen.

## Requirements

- Python 3.12 or newer
- Windows, macOS, or Linux with a graphical desktop

## Install and run from source

Clone the repository and install its dependencies:

```bash
git clone https://github.com/Wolfie192/TTRPGMapController.git
cd TTRPGMapController
python -m pip install .
python main.py
```

The file picker supports PNG, JPG/JPEG, BMP, and SVG maps. The app saves each map's last position, zoom, and rotation in `map_settings.json` in the current working directory.

## Controls

- Drag with the left mouse button to pan the map.
- Use the mouse wheel, scale slider, or `-` / `+` buttons to zoom.
- Hold Shift while clicking `-` / `+` to adjust zoom in larger steps.
- Select **Rotate 90°** to rotate the map, or **Re-Center Maps** to reset its position.
- Press **F** or **F11** on the player screen to toggle full-screen mode.

## Build a Windows executable

On Windows, run:

```bash
python build_exe.py
```

The build script uses PyInstaller to create a standalone executable in `dist/`. The executable bundles `styles.qss` with the application.

## Project dependencies

Dependencies are declared in `pyproject.toml` and pinned for repeatable installs in `uv.lock`.
