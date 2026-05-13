from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

class LibraryManager:
    def __init__(self, library_dir):
        self.library_dir = Path(library_dir)
        if not self.library_dir.exists():
            self.library_dir.mkdir(parents=True, exist_ok=True)

    def populate_folder_tree(self, tree_widget):
        """Populates a given Treeview widget with the library folder structure."""
        tree_widget.delete(*tree_widget.get_children())
        root_node = tree_widget.insert("", "end", text="Maps", open=True, tags=("dir",))
        
        nodes = {"": root_node} # Map relative path to treeview item ID
        # Sort by path to ensure parents are created before children
        for path in sorted(self.library_dir.rglob('*')):
            if path.is_dir():
                rel_path = str(path.relative_to(self.library_dir))
                parent_rel = str(Path(rel_path).parent)
                
                parent_id = nodes.get(parent_rel)
                if parent_id is None and parent_rel == ".": # Direct child
                    parent_id = root_node
                elif parent_id is None:
                    continue
                
                nodes[rel_path] = tree_widget.insert(parent_id, "end", text=path.name, tags=("dir",))

    def create_new_folder(self, tree_widget):
        selected_item = tree_widget.selection()
        if not selected_item:
            messagebox.showwarning("New Folder", "Please select a parent folder first.")
            return

        parent_id = selected_item[0]
        parts = []
        curr = parent_id
        while curr:
            txt = tree_widget.item(curr)["text"]
            if txt != "Maps": parts.insert(0, txt)
            curr = tree_widget.parent(curr)
        
        current_folder_path = self.library_dir.joinpath(*parts)
        new_folder_name = simpledialog.askstring("New Folder", "Enter new folder name:")
        
        if new_folder_name:
            new_full_path = current_folder_path / new_folder_name
            try:
                new_full_path.mkdir(exist_ok=True)
                self.populate_folder_tree(tree_widget)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")

    def save_map(self, folder_tree, name, map_data):
        selected_item = folder_tree.selection()
        if not selected_item:
            messagebox.showwarning("Save Map", "Please select a folder to save in.")
            return False

        if not name:
            messagebox.showwarning("Save Map", "Please enter a map name.")
            return False

        parent_id = selected_item[0]
        parts = []
        curr = parent_id
        while curr:
            txt = folder_tree.item(curr)["text"]
            if txt != "Maps": parts.insert(0, txt)
            curr = folder_tree.parent(curr)
        
        target_dir = self.library_dir.joinpath(*parts)
        file_path = target_dir / f"{name}.json"

        if file_path.exists():
            if not messagebox.askyesno("Overwrite?", f"Map '{name}' already exists. Overwrite?"):
                return False

        try:
            with file_path.open('w') as f:
                json.dump(map_data, f)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save map: {e}")
            return False

    def get_path_from_tree_item(self, tree_widget, item_id):
        parts = []
        curr = item_id
        while curr:
            txt = tree_widget.item(curr)["text"]
            if txt != "Maps": parts.insert(0, txt)
            curr = tree_widget.parent(curr)
        return str(self.library_dir.joinpath(*parts))
