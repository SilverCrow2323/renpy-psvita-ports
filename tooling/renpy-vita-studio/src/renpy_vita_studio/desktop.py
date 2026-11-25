"""Guided Tk desktop application for Linux and Windows."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from .builder import build_game_vpk
from .project_source import resolve_game_directory, discover_artwork, default_title_id
from .runtime_catalog import RUNTIMES
from .runtime_manager import get_installed_runtime
from .inspect import inspect_project

class StudioApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ren'Py Vita Studio")
        self.root.geometry("900x700")
        self.root.minsize(780, 620)
        self.root.configure(bg="#111827")
        self.project_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.title_id_var = tk.StringVar()
        self.runtime_var = tk.StringVar(value="renpy8-pvr")
        self.artwork_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Choose the original game folder to begin.")
        self.artwork_paths: list[Path] = []
        self._build_ui()
        self._refresh_runtime_status()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("DejaVu Sans", 10))
        style.configure("Header.TLabel", font=("DejaVu Sans", 20, "bold"), foreground="#f9fafb")
        style.configure("Sub.TLabel", foreground="#9ca3af")
        style.configure("TButton", padding=8)
        style.configure("TEntry", padding=6)
        style.configure("TRadiobutton", background="#111827", foreground="#e5e7eb")
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="REN'PY VITA STUDIO", style="Header.TLabel").pack(anchor="w")
        ttk.Label(outer, text="From original Ren'Py project to verified PlayStation Vita VPK", style="Sub.TLabel").pack(anchor="w", pady=(2,18))
        self.steps = ttk.Notebook(outer)
        self.steps.pack(fill="both", expand=True)
        self.project_tab = ttk.Frame(self.steps, padding=18)
        self.runtime_tab = ttk.Frame(self.steps, padding=18)
        self.art_tab = ttk.Frame(self.steps, padding=18)
        self.build_tab = ttk.Frame(self.steps, padding=18)
        self.steps.add(self.project_tab, text="1  GAME")
        self.steps.add(self.runtime_tab, text="2  RUNTIME")
        self.steps.add(self.art_tab, text="3  LIVEAREA")
        self.steps.add(self.build_tab, text="4  BUILD VPK")
        self._build_project_tab()
        self._build_runtime_tab()
        self._build_art_tab()
        self._build_build_tab()
        ttk.Label(outer, textvariable=self.status_var, style="Sub.TLabel").pack(anchor="w", pady=(14,0))

    def _build_project_tab(self):
        tab = self.project_tab
        ttk.Label(tab, text="Select the original game folder", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Choose the folder that contains game/. Do not prepare a Vita app folder and do not create sce_sys or LiveArea files yourself.", wraplength=760).pack(anchor="w", pady=(10,18))
        row = ttk.Frame(tab); row.pack(fill="x")
        ttk.Entry(row, textvariable=self.project_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self._browse_project).pack(side="left", padx=(8,0))
        ttk.Label(tab, text="Studio reads the selected project's game/ directory and ignores existing Vita packaging scaffolding.", style="Sub.TLabel", wraplength=740).pack(anchor="w", pady=14)
        ttk.Button(tab, text="Inspect game folder", command=self._inspect_project).pack(anchor="w")
        self.project_report = tk.Text(tab, height=13, bg="#0b1220", fg="#d1d5db", relief="flat", wrap="word")
        self.project_report.pack(fill="both", expand=True, pady=(14,0))

    def _build_runtime_tab(self):
        tab = self.runtime_tab
        ttk.Label(tab, text="Choose the Vita runtime", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Runtime files are managed by Studio. They are downloaded into its private cache the first time they are needed; you never browse for runtime folders.", wraplength=760).pack(anchor="w", pady=(8,14))
        self.runtime_desc = tk.Text(tab, height=12, bg="#0b1220", fg="#d1d5db", relief="flat", wrap="word")
        self.runtime_desc.pack(fill="both", expand=True, pady=(8,14))
        for key, profile in RUNTIMES.items():
            ttk.Radiobutton(tab, text=profile["name"], value=key, variable=self.runtime_var, command=self._refresh_runtime_status).pack(anchor="w", pady=5)
        self.runtime_state = ttk.Label(tab, text="")
        self.runtime_state.pack(anchor="w", pady=12)
        ttk.Button(tab, text="Refresh runtime status", command=self._refresh_runtime_status).pack(anchor="w")

    def _build_art_tab(self):
        tab = self.art_tab
        ttk.Label(tab, text="Generate the LiveArea", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Studio creates icon0, pic0, pic1 and the LiveArea background/startup images. Select an image already inside the game's data, or choose another image; cropping and resizing are automatic.", wraplength=760).pack(anchor="w", pady=(8,16))
        ttk.Label(tab, text="Game title").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.title_var).pack(fill="x", pady=(4,12))
        ttk.Label(tab, text="Vita Title ID (9 uppercase letters/numbers)").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.title_id_var).pack(fill="x", pady=(4,12))
        ttk.Label(tab, text="Artwork found in game/").pack(anchor="w")
        self.art_combo = ttk.Combobox(tab, textvariable=self.artwork_var, state="readonly")
        self.art_combo.pack(fill="x", pady=(4,8))
        row=ttk.Frame(tab); row.pack(fill="x")
        ttk.Button(row, text="Scan game artwork", command=self._scan_artwork).pack(side="left")
        ttk.Button(row, text="Use external image…", command=self._browse_artwork).pack(side="left", padx=8)
        ttk.Label(tab, text="If no suitable image exists, Studio generates a clean title card. Original game files are never modified.", style="Sub.TLabel", wraplength=740).pack(anchor="w", pady=18)

    def _build_build_tab(self):
        tab = self.build_tab
        ttk.Label(tab, text="Build your VPK", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Studio combines the selected game data with the managed runtime, generates Vita metadata and LiveArea assets, then runs VitaSDK's VPK packer and verifies the archive.", wraplength=760).pack(anchor="w", pady=(8,16))
        row=ttk.Frame(tab); row.pack(fill="x")
        ttk.Entry(row, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Choose VPK output…", command=self._browse_output).pack(side="left", padx=(8,0))
        self.log = tk.Text(tab, height=18, bg="#0b1220", fg="#d1d5db", relief="flat", wrap="word")
        self.log.pack(fill="both", expand=True, pady=14)
        self.build_button = ttk.Button(tab, text="BUILD VPK", command=self._start_build)
        self.build_button.pack(anchor="e")

    def _browse_project(self):
        path=filedialog.askdirectory(title="Select original Ren'Py game folder")
        if path:
            self.project_var.set(path)
            self._inspect_project()

    def _inspect_project(self):
        try:
            root, game=resolve_game_directory(self.project_var.get())
            files=[p for p in game.rglob("*") if p.is_file() and not p.is_symlink()]
            size=sum(p.stat().st_size for p in files)
            title=root.name.replace("_"," ").replace("-"," ").strip() or "Ren'Py Game"
            self.title_var.set(title)
            self.title_id_var.set(default_title_id(title, root))
            report=inspect_project(root)
            self.project_report.delete("1.0","end")
            self.project_report.insert("end", f"Project: {root}\nGame data: {game}\nFiles: {len(files):,}\nSize: {size/1024/1024:.1f} MiB\n")
            self.project_report.insert("end", "\nCompatibility preflight (not a guarantee):\n")
            for hint in report.get("compatibility_hints", []):
                self.project_report.insert("end", "• "+str(hint)+"\n")
            if report.get("video_files"):
                self.project_report.insert("end", f"\nVideo files detected: {len(report['video_files'])} — the Vita runtime does not provide general video playback.\n")
            if report.get("native_libraries"):
                self.project_report.insert("end", f"Native libraries detected: {len(report['native_libraries'])} — desktop binaries cannot be assumed to work on Vita.\n")
            self.project_report.insert("end", "\nOnly game/ will be copied. Existing sce_sys, eboot.bin or LiveArea folders are not required.\n")
            self._scan_artwork()
            self.status_var.set("Game folder detected. Review the compatibility notes, then choose a runtime.")
        except Exception as exc:
            messagebox.showerror("Project inspection", str(exc))

    def _refresh_runtime_status(self):
        key=self.runtime_var.get()
        profile=RUNTIMES[key]
        installed=get_installed_runtime(key)
        state="Already downloaded and ready" if installed else "Not downloaded yet — Studio will download it when you build."
        self.runtime_state.configure(text=state)
        self.runtime_desc.delete("1.0","end")
        self.runtime_desc.insert("end", profile["description"]+"\n\n"+profile["warning"]+"\n\nSource: "+profile["source"])

    def _scan_artwork(self):
        try:
            _root, game=resolve_game_directory(self.project_var.get())
            self.artwork_paths=discover_artwork(game)
            self.art_combo["values"]=[str(p.relative_to(game)) for p in self.artwork_paths]
            if self.artwork_paths:
                self.artwork_var.set(str(self.artwork_paths[0].relative_to(game)))
            else:
                self.artwork_var.set("")
            self.status_var.set(f"Found {len(self.artwork_paths)} possible artwork files.")
        except Exception as exc:
            messagebox.showerror("Artwork scan", str(exc))

    def _browse_artwork(self):
        path=filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.webp *.bmp"),("All files","*.*")])
        if path:
            self.artwork_var.set(path)

    def _browse_output(self):
        name=(self.title_var.get().strip() or "RenPyGame").replace("/","-")
        path=filedialog.asksaveasfilename(defaultextension=".vpk",initialfile=name+".vpk",filetypes=[("PlayStation Vita package","*.vpk")])
        if path:
            self.output_var.set(path)

    def _selected_artwork(self):
        value=self.artwork_var.get().strip()
        if not value:
            return None
        candidate=Path(value)
        if candidate.is_absolute():
            return candidate
        _root, game=resolve_game_directory(self.project_var.get())
        return game / candidate

    def _start_build(self):
        try:
            resolve_game_directory(self.project_var.get())
            title=self.title_var.get().strip()
            title_id=self.title_id_var.get().strip()
            project=self.project_var.get()
            runtime_id=self.runtime_var.get()
            artwork=self._selected_artwork()
            output=self.output_var.get().strip()
            if not title:
                raise ValueError("Enter a game title.")
            if not title_id:
                raise ValueError("Enter a Vita Title ID.")
            if not output:
                self._browse_output()
                output=self.output_var.get().strip()
            if not output:
                return
            self.build_button.configure(state="disabled")
            self.log.delete("1.0","end")
            def progress(message):
                self.root.after(0, lambda msg=message: self._log(msg))
            def worker():
                try:
                    result=build_game_vpk(project,runtime_id,title,title_id,output,artwork,progress)
                    self.root.after(0,lambda res=result:self._build_done(res))
                except Exception as exc:
                    self.root.after(0,lambda err=str(exc):self._build_failed(err))
            threading.Thread(target=worker,daemon=True).start()
        except Exception as exc:
            messagebox.showerror("Build",str(exc))

    def _log(self,message):
        self.log.insert("end",message+"\n"); self.log.see("end"); self.status_var.set(message)

    def _build_done(self,result):
        self.build_button.configure(state="normal")
        self._log("VPK created and archive verification passed.")
        self._log("Output: "+result["vpk"]["output"])
        self._log("SHA-256: "+result["sha256"])
        self._log("Build report: "+result["manifest"])
        messagebox.showinfo("VPK ready","VPK created and verified.\n\n"+result["vpk"]["output"]+"\n\nInstallation and runtime execution still need a real PS Vita test.")

    def _build_failed(self,error):
        self.build_button.configure(state="normal")
        self._log("ERROR: "+error)
        messagebox.showerror("VPK build failed",error)

def main():
    root=tk.Tk()
    StudioApp(root)
    root.mainloop()

if __name__=="__main__":
    main()
