import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream

from control_screen import ControlScreen
from player_screen import PlayerScreen

class MapControllerApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        stylesheet_path = resource_path(Path("./styles.qss"))
        self._load_stylesheet(str(stylesheet_path))

        self.control_screen = ControlScreen()
        self.player_screen = PlayerScreen()

        self.control_screen.map_loaded.connect(self.player_screen.load_map)
        self.control_screen.view_state_changed.connect(self.player_screen.update_map_view)

        self.control_screen.closing.connect(self._on_control_screen_closing)

        self.control_screen.show()
        self.player_screen.show()

    def _load_stylesheet(self, path):
        file = QFile(path)
        if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            print(f"Warning: Could not open stylesheet file {path}: {file.errorString()}")
            return

        stream = QTextStream(file)
        self.setStyleSheet(stream.readAll())
        file.close()

    def _on_control_screen_closing(self):
        self.player_screen.close()
        self.quit()

def resource_path(relative_path):
    # PyInstaller extracts bundled resources to _MEIPASS. When running from
    # source, resolve them beside this file rather than from the shell's cwd.
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

    return base_path / relative_path

if __name__ == "__main__":
    app = MapControllerApp(sys.argv)
    sys.exit(app.exec())
