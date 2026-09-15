"""Tkinter interface for FolderOrganizer."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import build_preview, organize_preview, undo_last_run


def completion_message(moved_count: int) -> str:
    return f"Ding! Complete — organized {moved_count} file(s). Use Undo Last Run to restore them."


class FolderOrganizerApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=16)
        self.master = master
        self.folder: Path | None = None
        self.status = tk.StringVar(value="Choose a folder to create a local preview.")
        self._build()

    def _build(self) -> None:
        self.master.title("FolderOrganizer")
        self.master.minsize(640, 430)
        self.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="Choose Folder…", command=self.choose_folder).pack(side=tk.LEFT)
        self.organize_button = ttk.Button(toolbar, text="Organize", command=self.organize)
        self.organize_button.pack(side=tk.LEFT, padx=(8, 0))
        self.undo_button = ttk.Button(toolbar, text="Undo Last Run", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=(8, 0))

        self.folder_label = ttk.Label(self, text="No folder selected", wraplength=600)
        self.folder_label.pack(fill=tk.X, pady=(14, 6))
        self.preview_text = tk.Text(self, height=16, state=tk.DISABLED, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        ttk.Label(self, textvariable=self.status, wraplength=600).pack(fill=tk.X, pady=(10, 0))

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(parent=self.master, title="Select a folder to organize")
        if not selected:
            self.status.set("Folder selection cancelled. No files changed.")
            return
        self.folder = Path(selected)
        self.folder_label.configure(text=str(self.folder))
        self.show_preview()

    def show_preview(self) -> None:
        if self.folder is None:
            return
        try:
            preview = build_preview(self.folder)
        except OSError as error:
            self._show_error(f"Could not read the selected folder: {error}")
            return
        lines = ["Preview only — nothing has been moved.", ""]
        if preview.file_count:
            for extension, names in preview.groups.items():
                lines.append(f"{extension} ({len(names)} file(s))")
                lines.extend(f"  • {name}" for name in names)
        else:
            lines.append("No eligible top-level files found.")
        lines.append("")
        lines.append(f"Excluded {preview.excluded_count} hidden item(s) or folder(s).")
        self._set_preview("\n".join(lines))
        self.status.set(f"Preview: {preview.file_count} eligible file(s).")

    def organize(self) -> None:
        if self.folder is None:
            self._show_error("Choose a folder before organizing.")
            return
        preview = build_preview(self.folder)
        if preview.file_count == 0:
            self.status.set("Nothing eligible to organize. No files changed.")
            return
        confirmed = messagebox.askyesno(
            "Confirm organization",
            f"Move {preview.file_count} visible top-level file(s) into extension folders?\n\n"
            "This changes files locally. An undo manifest will be created.",
            parent=self.master,
        )
        if not confirmed:
            self.status.set("Organization cancelled. No files changed.")
            return
        try:
            result = organize_preview(self.folder, confirmed=True)
        except OSError as error:
            self._show_error(f"Organization stopped: {error}")
            return
        self.show_preview()
        self.status.set(completion_message(len(result.moves)))

    def undo(self) -> None:
        if self.folder is None:
            self._show_error("Choose the folder used for the previous run before undoing.")
            return
        if not messagebox.askyesno(
            "Confirm undo",
            "Restore files from this folder's last-run manifest? Existing files will never be overwritten.",
            parent=self.master,
        ):
            self.status.set("Undo cancelled. No files changed.")
            return
        try:
            result = undo_last_run(self.folder)
        except (OSError, ValueError) as error:
            self._show_error(f"Undo stopped: {error}")
            return
        self.show_preview()
        self.status.set(result.message)

    def _set_preview(self, text: str) -> None:
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.configure(state=tk.DISABLED)

    def _show_error(self, message: str) -> None:
        self.status.set(message)
        messagebox.showerror("FolderOrganizer", message, parent=self.master)


def main() -> None:
    root = tk.Tk()
    FolderOrganizerApp(root)
    root.mainloop()
