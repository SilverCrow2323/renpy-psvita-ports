"""Guided Tk desktop application for Linux and Windows."""
from __future__ import annotations
import threading
import tkinter as tk
from tkinter import filedialog,messagebox,ttk
from pathlib import Path
from .builder import build_game_vpk
from .project_source import resolve_game_directory,discover_artwork,default_title_id
from .runtime_catalog import RUNTIMES
from .runtime_manager import get_installed_runtime
from .inspect import inspect_project

ART_SLOTS={"Bubble icon":"icon0","Boot screen":"pic0","LiveArea background":"bg0","Startup artwork":"startup"}

class StudioApp:
    def __init__(self,root: tk.Tk):
        self.root=root; root.title("Ren'Py Vita Studio"); root.geometry("920x740"); root.minsize(800,650); root.configure(bg="#111827")
        self.project_var=tk.StringVar(); self.title_var=tk.StringVar(); self.title_id_var=tk.StringVar()
        self.app_version_var=tk.StringVar(value="01.00"); self.runtime_var=tk.StringVar(value="renpy8-pvr")
        self.output_var=tk.StringVar(); self.status_var=tk.StringVar(value="Choose the original game folder to begin.")
        self.art_vars={label:tk.StringVar() for label in ART_SLOTS}; self.art_slot_var=tk.StringVar(value="Bubble icon")
        self.artwork_paths=[]; self._build_ui(); self._refresh_runtime_status()

    def _build_ui(self):
        style=ttk.Style(); style.theme_use("clam")
        style.configure("TFrame",background="#111827"); style.configure("TLabel",background="#111827",foreground="#e5e7eb",font=("DejaVu Sans",10))
        style.configure("Header.TLabel",font=("DejaVu Sans",20,"bold"),foreground="#f9fafb"); style.configure("Sub.TLabel",foreground="#9ca3af")
        style.configure("TButton",padding=8); style.configure("TEntry",padding=6); style.configure("TRadiobutton",background="#111827",foreground="#e5e7eb")
        outer=ttk.Frame(self.root,padding=22); outer.pack(fill="both",expand=True)
        ttk.Label(outer,text="REN'PY VITA STUDIO",style="Header.TLabel").pack(anchor="w")
        ttk.Label(outer,text="From original Ren'Py project to verified PlayStation Vita VPK",style="Sub.TLabel").pack(anchor="w",pady=(2,18))
        self.steps=ttk.Notebook(outer); self.steps.pack(fill="both",expand=True)
        self.project_tab=ttk.Frame(self.steps,padding=18); self.runtime_tab=ttk.Frame(self.steps,padding=18)
        self.art_tab=ttk.Frame(self.steps,padding=18); self.build_tab=ttk.Frame(self.steps,padding=18)
        for tab,label in ((self.project_tab,"1  GAME"),(self.runtime_tab,"2  RUNTIME"),(self.art_tab,"3  LIVEAREA"),(self.build_tab,"4  BUILD VPK")): self.steps.add(tab,text=label)
        self._build_project_tab(); self._build_runtime_tab(); self._build_art_tab(); self._build_build_tab()
        ttk.Label(outer,textvariable=self.status_var,style="Sub.TLabel").pack(anchor="w",pady=(14,0))

    def _build_project_tab(self):
        tab=self.project_tab
        ttk.Label(tab,text="Select the original game folder",style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab,text="Choose the folder that contains game/, or select game/ itself. Do not prepare a Vita app folder or create sce_sys/ or LiveArea files.",wraplength=760).pack(anchor="w",pady=(10,18))
        row=ttk.Frame(tab); row.pack(fill="x"); ttk.Entry(row,textvariable=self.project_var).pack(side="left",fill="x",expand=True)
        ttk.Button(row,text="Browse…",command=self._browse_project).pack(side="left",padx=(8,0))
        ttk.Label(tab,text="Only the game's game/ directory is copied. Old Vita scaffolding and unrelated project files are ignored.",style="Sub.TLabel",wraplength=740).pack(anchor="w",pady=14)
        ttk.Button(tab,text="Inspect game folder",command=self._inspect_project).pack(anchor="w")
        self.project_report=tk.Text(tab,height=14,bg="#0b1220",fg="#d1d5db",relief="flat",wrap="word"); self.project_report.pack(fill="both",expand=True,pady=(14,0))

    def _build_runtime_tab(self):
        tab=self.runtime_tab; ttk.Label(tab,text="Choose the Vita runtime",style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab,text="Studio manages runtime downloads and caches them privately. You never browse for local runtime files.",wraplength=760).pack(anchor="w",pady=(8,14))
        self.runtime_desc=tk.Text(tab,height=12,bg="#0b1220",fg="#d1d5db",relief="flat",wrap="word"); self.runtime_desc.pack(fill="both",expand=True,pady=(8,14))
        for key,profile in RUNTIMES.items(): ttk.Radiobutton(tab,text=profile["name"],value=key,variable=self.runtime_var,command=self._refresh_runtime_status).pack(anchor="w",pady=5)
        self.runtime_state=ttk.Label(tab,text=""); self.runtime_state.pack(anchor="w",pady=12)
        ttk.Button(tab,text="Refresh runtime status",command=self._refresh_runtime_status).pack(anchor="w")

    def _build_art_tab(self):
        tab=self.art_tab; ttk.Label(tab,text="LiveArea and app metadata",style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab,text="Choose separate artwork for the bubble icon, boot screen, LiveArea background and startup image. Studio crops, resizes and optimizes each asset automatically.",wraplength=760).pack(anchor="w",pady=(8,14))
        for label,var in (("Game title",self.title_var),("Vita Title ID (9 characters)",self.title_id_var),("App version (XX.XX)",self.app_version_var)):
            ttk.Label(tab,text=label).pack(anchor="w"); ttk.Entry(tab,textvariable=var).pack(fill="x",pady=(4,9))
        ttk.Button(tab,text="Scan images in game/",command=self._scan_artwork).pack(anchor="w",pady=(4,10))
        self.art_combos={}
        for label,var in self.art_vars.items():
            row=ttk.Frame(tab); row.pack(fill="x",pady=4)
            ttk.Label(row,text=label,width=22).pack(side="left")
            combo=ttk.Combobox(row,textvariable=var,state="readonly"); combo.pack(side="left",fill="x",expand=True)
            self.art_combos[label]=combo
        row=ttk.Frame(tab); row.pack(fill="x",pady=(12,0))
        ttk.Label(row,text="External image for:").pack(side="left")
        ttk.Combobox(row,textvariable=self.art_slot_var,values=list(ART_SLOTS),state="readonly",width=22).pack(side="left",padx=8)
        ttk.Button(row,text="Browse external image…",command=self._browse_artwork).pack(side="left")
        ttk.Label(tab,text="Any slot left empty gets a generated title card. Original game assets are never modified.",style="Sub.TLabel",wraplength=740).pack(anchor="w",pady=12)

    def _build_build_tab(self):
        tab=self.build_tab; ttk.Label(tab,text="Build your VPK",style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab,text="Studio combines game data and the selected runtime, generates SFO and LiveArea assets, then creates and verifies the VPK with VitaSDK.",wraplength=760).pack(anchor="w",pady=(8,16))
        row=ttk.Frame(tab); row.pack(fill="x"); ttk.Entry(row,textvariable=self.output_var).pack(side="left",fill="x",expand=True)
        ttk.Button(row,text="Choose VPK output…",command=self._browse_output).pack(side="left",padx=(8,0))
        self.log=tk.Text(tab,height=18,bg="#0b1220",fg="#d1d5db",relief="flat",wrap="word"); self.log.pack(fill="both",expand=True,pady=14)
        self.build_button=ttk.Button(tab,text="BUILD VPK",command=self._start_build); self.build_button.pack(anchor="e")

    def _browse_project(self):
        path=filedialog.askdirectory(title="Select original Ren'Py game folder")
        if path: self.project_var.set(path); self._inspect_project()

    def _inspect_project(self):
        try:
            root,game=resolve_game_directory(self.project_var.get()); files=[p for p in game.rglob("*") if p.is_file() and not p.is_symlink()]
            size=sum(p.stat().st_size for p in files); title=root.name.replace("_"," ").replace("-"," ").strip() or "Ren'Py Game"
            self.title_var.set(title); self.title_id_var.set(default_title_id(title,root))
            report=inspect_project(root); self.project_report.delete("1.0","end")
            self.project_report.insert("end",f"Project: {root}\nGame data: {game}\nFiles: {len(files):,}\nSize: {size/1024/1024:.1f} MiB\n")
            self.project_report.insert("end","\nCompatibility preflight (not a guarantee):\n")
            for hint in report.get("compatibility_hints",[]): self.project_report.insert("end","• "+str(hint)+"\n")
            if report.get("video_files"): self.project_report.insert("end",f"\nVideo files detected: {len(report['video_files'])} — general video playback is not supported by the referenced runtimes.\n")
            if report.get("native_libraries"): self.project_report.insert("end",f"Native libraries detected: {len(report['native_libraries'])} — desktop binaries cannot be assumed to work on Vita.\n")
            self.project_report.insert("end","\nOnly game/ will be copied. Existing sce_sys, eboot.bin or LiveArea folders are not required.\n")
            self._scan_artwork(); self.status_var.set("Game folder detected. Review compatibility notes and choose a runtime.")
        except Exception as exc: messagebox.showerror("Project inspection",str(exc))

    def _refresh_runtime_status(self):
        key=self.runtime_var.get(); profile=RUNTIMES[key]; installed=get_installed_runtime(key)
        self.runtime_state.configure(text="Already downloaded and ready" if installed else "Not downloaded yet — Studio downloads it on first use.")
        self.runtime_desc.delete("1.0","end")
        self.runtime_desc.insert("end",profile["description"]+"\n\n"+profile["warning"]+"\n\nSource: "+profile["source"])

    def _scan_artwork(self):
        try:
            _root,game=resolve_game_directory(self.project_var.get()); self.artwork_paths=discover_artwork(game)
            values=[str(p.relative_to(game)) for p in self.artwork_paths]
            for label,var in self.art_vars.items():
                self.art_combos[label]["values"]=values
                if values and not var.get(): var.set(values[0])
            self.status_var.set(f"Found {len(self.artwork_paths)} possible artwork files.")
        except Exception as exc: messagebox.showerror("Artwork scan",str(exc))

    def _browse_artwork(self):
        path=filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.webp *.bmp"),("All files","*.*")])
        if path: self.art_vars[self.art_slot_var.get()].set(path)

    def _browse_output(self):
        name=(self.title_var.get().strip() or "RenPyGame").replace("/","-")
        path=filedialog.asksaveasfilename(defaultextension=".vpk",initialfile=name+".vpk",filetypes=[("PlayStation Vita package","*.vpk")])
        if path: self.output_var.set(path)

    def _selected_artwork(self):
        _root,game=resolve_game_directory(self.project_var.get()); selected={}
        for label,var in self.art_vars.items():
            value=var.get().strip()
            if value:
                path=Path(value); selected[ART_SLOTS[label]]=path if path.is_absolute() else game/path
        return selected

    def _start_build(self):
        try:
            resolve_game_directory(self.project_var.get()); title=self.title_var.get().strip(); title_id=self.title_id_var.get().strip()
            app_version=self.app_version_var.get().strip(); project=self.project_var.get(); runtime_id=self.runtime_var.get()
            artwork=self._selected_artwork(); output=self.output_var.get().strip()
            if not title: raise ValueError("Enter a game title.")
            if not title_id: raise ValueError("Enter a Vita Title ID.")
            if not output: self._browse_output(); output=self.output_var.get().strip()
            if not output: return
            self.build_button.configure(state="disabled"); self.log.delete("1.0","end")
            def progress(message): self.root.after(0,lambda msg=message:self._log(msg))
            def worker():
                try:
                    result=build_game_vpk(project,runtime_id,title,title_id,output,artwork,progress,app_version)
                    self.root.after(0,lambda res=result:self._build_done(res))
                except Exception as exc: self.root.after(0,lambda err=str(exc):self._build_failed(err))
            threading.Thread(target=worker,daemon=True).start()
        except Exception as exc: messagebox.showerror("Build",str(exc))

    def _log(self,message):
        self.log.insert("end",message+"\n"); self.log.see("end"); self.status_var.set(message)

    def _build_done(self,result):
        self.build_button.configure(state="normal"); self._log("VPK created and archive verification passed.")
        self._log("Output: "+result["vpk"]["output"]); self._log("SHA-256: "+result["sha256"]); self._log("Build report: "+result["manifest"])
        messagebox.showinfo("VPK ready","VPK created and verified.\n\n"+result["vpk"]["output"]+"\n\nInstallation and runtime execution still need a real PS Vita test.")

    def _build_failed(self,error):
        self.build_button.configure(state="normal"); self._log("ERROR: "+error); messagebox.showerror("VPK build failed",error)

def main():
    root=tk.Tk(); StudioApp(root); root.mainloop()

if __name__=="__main__": main()
