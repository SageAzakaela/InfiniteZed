import tkinter as tk
from tkinter import filedialog

def _label(p, t): return tk.Label(p, text=t, bg="#121212", fg="white")

class ExportTab(tk.Frame):
    def __init__(self, parent, conf, on_change, on_click):
        super().__init__(parent, bg="#121212")
        self.conf = conf
        self.on_change = on_change
        self.on_click = on_click

        self.var_outdir = tk.StringVar(value=conf.get("output_dir", "output"))
        _label(self, "Output folder").pack(anchor="w", padx=8, pady=(8, 0))
        ent = tk.Entry(self, textvariable=self.var_outdir, bg="#1e1e1e", fg="white", insertbackground="white")
        ent.pack(fill=tk.X, padx=8, pady=(0, 6))
        ent.bind("<KeyRelease>", lambda _e: self._write_back())

        br = tk.Button(self, text="Browse…", command=self._browse)
        br.pack(anchor="w", padx=8, pady=(0, 10))

        _label(self, "Filenames").pack(anchor="w", padx=8, pady=(4, 0))
        exp = conf.setdefault("export", {
            "terrain_png": "terrain.png",
            "vegetation_png": "vegetation.png",
            "roads_png": "roads.png",
            "combined_png": "preview.png",
            "lots_png": "lots.png",
        })

        self.entries = {}
        for key in ["terrain_png","vegetation_png","roads_png","combined_png","lots_png"]:
            row = tk.Frame(self, bg="#121212"); row.pack(fill=tk.X, padx=8, pady=(2,0))
            _label(row, key).pack(side=tk.LEFT)
            var = tk.StringVar(value=exp.get(key, ""))
            ent = tk.Entry(row, width=24, textvariable=var, bg="#1e1e1e", fg="white", insertbackground="white")
            ent.pack(side=tk.LEFT, padx=(6,0))
            ent.bind("<KeyRelease>", lambda _e, k=key, v=var: self._write_file(k, v))
            self.entries[key] = var

    def _browse(self):
        d = filedialog.askdirectory()
        if not d: return
        self.var_outdir.set(d)
        self._write_back()

    def _write_back(self):
        self.conf["output_dir"] = self.var_outdir.get()
        self.on_change()

    def _write_file(self, key, var):
        self.conf.setdefault("export", {})[key] = var.get()
        self.on_change()

    def apply_conf(self, conf):
        self.conf = conf
        self.var_outdir.set(conf.get("output_dir","output"))
        exp = conf.setdefault("export", {})
        for key, var in self.entries.items():
            var.set(exp.get(key,var.get()))
