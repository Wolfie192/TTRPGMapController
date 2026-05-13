import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from pathlib import Path

class LibraryDialogs:
    @staticmethod
    def show_save_dialog(parent, library_manager, image_path, scale, map_x, map_y):
        save_win = tk.Toplevel(parent)
        save_win.title("Save to Library")
        save_win.geometry("500x400")
        save_win.transient(parent)
        save_win.grab_set()

        paned = tk.PanedWindow(save_win, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        folder_tree = ttk.Treeview(paned, selectmode="browse")
        folder_tree.heading("#0", text="Folders", anchor=tk.W)
        paned.add(folder_tree, width=250)

        right_frame = tk.Frame(paned)
        paned.add(right_frame, width=350)

        tk.Label(right_frame, text="Map Name:").pack(pady=(10, 0))
        name_ent = tk.Entry(right_frame, width=40)
        name_ent.pack(pady=5)

        tk.Button(right_frame, text="New Folder", 
                  command=lambda: library_manager.create_new_folder(folder_tree)).pack(pady=5)

        def commit():
            map_data = {
                "image_path": image_path,
                "scale": scale,
                "last_x": map_x,
                "last_y": map_y
            }
            if library_manager.save_map(folder_tree, name_ent.get().strip(), map_data):
                save_win.destroy()

        tk.Button(right_frame, text="Save Map", command=commit).pack(pady=10)

        library_manager.populate_folder_tree(folder_tree)

    @staticmethod
    def show_browser_dialog(parent, library_manager, on_map_selected):
        browser = tk.Toplevel(parent)
        browser.title("Library Browser")
        browser.geometry("800x450")

        paned = tk.PanedWindow(browser, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(paned, selectmode="browse")
        tree.heading("#0", text="Library Folders", anchor=tk.W)
        paned.add(tree, width=250)
        
        file_view = ttk.Treeview(paned, columns=("name", "scale"), show="headings")
        file_view.heading("name", text="Map Name")
        file_view.heading("scale", text="Scale")
        file_view.heading("scale", width=80, anchor=tk.CENTER)
        paned.add(file_view, width=600)
        
        map_registry = {}

        def on_folder_select(event):
            file_view.delete(*file_view.get_children())
            map_registry.clear()
            
            selected = tree.selection()
            if not selected: return
            
            target_path = library_manager.get_path_from_tree_item(tree, selected[0])
            target_path_obj = Path(target_path)
            if not target_path_obj.exists(): return
            
            for f_path in target_path_obj.glob("*.json"):
                try:
                    with f_path.open('r') as jf:
                        data = json.load(jf)
                        iid = file_view.insert("", "end", values=(f_path.stem, data.get("scale", 1.0)))
                        map_registry[iid] = data
                except Exception:
                    continue

        def on_select(event):
            selected = file_view.selection()
            if not selected: return
            data = map_registry.get(selected[0])
            if data:
                on_map_selected(data)
                browser.destroy()

        tree.bind("<<TreeviewSelect>>", on_folder_select)
        file_view.bind("<Double-1>", on_select)
        tk.Button(browser, text="Load Selected Map", command=lambda: on_select(None)).pack(pady=5)