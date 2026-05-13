import tkinter as tk
import sys
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path

from core.monitor import MonitorManager
from core.library import LibraryManager
from ui.dialogs import LibraryDialogs

class MapApp:
    def __init__(self, root):
        # Determine Base Directory
        if getattr(sys, 'frozen', False):
            # If running as a bundled executable
            self.base_dir = Path(sys.executable).parent
            self.internal_res = Path(sys._MEIPASS)
        else:
            # If running in a normal Python environment
            self.base_dir = Path(__file__).parent
            self.internal_res = self.base_dir

        self.root = root
        self.root.title("TTRPG Map Tools - GM Control")
        
        # Calibration Settings
        self.player_scale = 4.0

        # State
        self.image_path = None
        self.original_image = None
        self.scaled_player_base = None
        self.player_photo = None
        self.gm_photo = None

        self.map_x, self.map_y = 0, 0
        self.gm_view_scale = 0.5
        self._debounce_id = None

        # Library & System Managers - Store maps relative to the EXE
        self.library_dir = self.base_dir / "library"
        self.library_manager = LibraryManager(self.library_dir)

        self.setup_gm_ui()
        self.create_player_window()

    def setup_gm_ui(self):
        # Main Menu Area
        menu_bar = tk.Frame(self.root)
        menu_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # File/Library Controls
        file_tools = tk.LabelFrame(menu_bar, text="Library & Files")
        file_tools.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(file_tools, text="Import New Image", command=self.load_map).pack(side=tk.LEFT, padx=2)
        tk.Button(file_tools, text="Save to Library", command=self.save_to_library, bg="#e1f5fe").pack(side=tk.LEFT, padx=2)
        tk.Button(file_tools, text="Open Library", command=self.open_library_browser).pack(side=tk.LEFT, padx=2)

        # Scaling Controls
        toolbar = tk.LabelFrame(menu_bar, text="Map Scaling")
        toolbar.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        tk.Label(toolbar, text="Map Scale:").pack(side=tk.LEFT, padx=(10, 0))
        self.scale_slider = tk.Scale(toolbar, from_=0.1, to=5.0, resolution=0.01, orient = tk.HORIZONTAL, length = 200, command = self.on_slider_move)
        self.scale_slider.set(self.player_scale)
        self.scale_slider.pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Finalize Quality", command=self.finalize_scaling).pack(side=tk.LEFT, padx=5)

        # GM Canvas (Preview)
        self.gm_canvas = tk.Canvas(self.root, bg="#333", width=600, height=400)
        self.gm_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.gm_canvas.bind("<Button-1>", self.start_pan)
        self.gm_canvas.bind("<B1-Motion>", self.do_pan)
        self.gm_canvas.bind("<MouseWheel>", self.handle_zoom)
        self.gm_canvas.bind("<Button-4>", self.handle_zoom)
        self.gm_canvas.bind("<Button-5>", self.handle_zoom)
        
        tk.Label(self.root, text="Left-click drag to pan. Mouse wheel to zoom.", 
                 fg="gray").pack(side=tk.BOTTOM)

    def create_player_window(self):
        self.player_win = tk.Toplevel(self.root)
        self.player_win.title("Player Map Display")
        self.player_win.geometry("800x600+200+200")
        self.player_win.configure(bg="black")
        
        self.player_canvas = tk.Canvas(self.player_win, bg="black", highlightthickness=0)
        self.player_canvas.pack(fill=tk.BOTH, expand=True)

    def save_to_library(self):
        """Opens the dialog to save the current map state to the library."""
        LibraryDialogs.show_save_dialog(
            self.root,
            self.library_manager,
            self.image_path,
            self.scale_slider.get(),
            self.map_x,
            self.map_y
        )

    def open_library_browser(self):
        def on_map_selected(data):
            self.image_path = data["image_path"]
            self.original_image = Image.open(self.image_path)

            saved_scale = data.get("scale", 1.0)
            self.scale_slider.set(saved_scale)
            self.player_scale = saved_scale

            self.map_x = data.get("last_x", 0)
            self.map_y = data.get("last_y", 0)

            self.finalize_scaling()

        LibraryDialogs.show_browser_dialog(self.root, self.library_manager, on_map_selected)

    def load_map(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp *.webp")])
        if path:
            self.image_path = path
            self.original_image = Image.open(path)
            self.finalize_scaling()

    def on_slider_move(self, event):
        """Handles slider movement with a fast preview and debounced high-quality render."""
        if self._debounce_id:
            self.root.after_cancel(self._debounce_id)

        # Fast Preview
        self.render_preview()
        # Schedule High Quality
        self._debounce_id = self.root.after(300, self.finalize_scaling)

    def render_preview(self):
        """Fast preview scaling using Bilinear while moving the slider."""
        if not self.original_image: return
        self.player_scale = self.scale_slider.get()
        new_w = int(self.original_image.width * self.player_scale)
        new_h= int(self.original_image.height * self.player_scale)
        
        self.scaled_player_base = self.original_image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        self.player_photo = ImageTk.PhotoImage(self.scaled_player_base)
        self.update_gm_preview()

    def finalize_scaling(self):
        """High-quality scaling using Lanczos."""
        if not self.original_image: return

        self.player_scale = self.scale_slider.get()
        new_w = int(self.original_image.width * self.player_scale)
        new_h = int(self.original_image.height * self.player_scale)
        self.scaled_player_base = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.player_photo = ImageTk.PhotoImage(self.scaled_player_base)

        self.update_gm_preview()

    def update_gm_preview(self):
        if not self.scaled_player_base:
            return

        gm_w = int(self.scaled_player_base.width * self.gm_view_scale)
        gm_h = int(self.scaled_player_base.height * self.gm_view_scale)

        gm_img = self.scaled_player_base.resize((gm_w, gm_h), Image.Resampling.BILINEAR)
        self.gm_photo = ImageTk.PhotoImage(gm_img)
        self.render()

    def handle_zoom(self, event):
        if event.num == 4 or event.delta > 0:
            self.gm_view_scale *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.gm_view_scale /= 1.1
        
        self.gm_view_scale = max(0.01, min(self.gm_view_scale, 5.0))
        self.update_gm_preview()

    def start_pan(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def do_pan(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        self.map_x += dx / self.gm_view_scale
        self.map_y += dy / self.gm_view_scale
        
        self.last_x = event.x
        self.last_y = event.y
        self.render()

    def render(self):
        self.gm_canvas.delete("all")
        self.player_canvas.delete("all")
        
        if self.player_photo:
            self.player_canvas.create_image(self.map_x, self.map_y, anchor=tk.NW, image=self.player_photo)
            self.gm_canvas.create_image(self.map_x * self.gm_view_scale, 
                                        self.map_y * self.gm_view_scale, 
                                        anchor=tk.NW, image=self.gm_photo)

if __name__ == "__main__":
    MonitorManager.set_dpi_awareness()
    root = tk.Tk()
    app = MapApp(root)
    root.mainloop()
