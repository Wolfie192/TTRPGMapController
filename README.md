# TTRPG Map Controller

A Python-based tool for controlling TTRPG maps.

## Prerequisites

- **Python 3.12+**
- **pip** (Python package installer).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ttrpg-map-controller.git
   cd "ttrpg-map-controller"
   ```

2. Install the required dependencies:
   ```bash
   pip install .
   ```
   *This will install `pillow` and `pyinstaller` as defined in your project configuration.*

## Building the Executable

To package the application into a single standalone `.exe` file for Windows:

1. Run the build script:
   ```bash
   python build_exe.py
   ```
2. Once finished, find your executable in the `dist/` folder named `TTRPG_MapTool.exe`.

## Running from Source

If you prefer to run the script directly without building an executable:
```bash
python main.py
```