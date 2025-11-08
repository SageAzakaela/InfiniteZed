import tkinter as tk
from tkinter import ttk

def _label(p, t): return tk.Label(p, text=t, bg="#121212", fg="white")

class VegetationTab(tk.Frame):
    PRESETS = {
        "overgrown": dict(scale=50, octaves=5, persistence=0.55, lacunarity=2.0, respect_terrain=True),
        "rural":     dict(scale=60, octaves=4, persistence=0.52, lacunarity=2.0, respect_terrain=True),
        "suburban":  dict(scale=45, octaves=6, persistence=0.50, lacunarity=2.2, respect_terrain=True),
    }

    def __init__(self, parent, conf, on_change, on_click):
        super().__init__(parent, bg="#121212")
        self.conf = conf
        self.on_change = on_change
        self.on_click = on_click
        veg = self.conf.setdefault("vegetation", {})

        row = tk.Frame(self, bg="#121212"); row.pack(fill=tk.X, padx=8, pady=(8, 4))
        _label(row, "Preset").pack(side=tk.LEFT)
        self.var_preset = tk.StringVar(value=veg.get("preset", "overgrown"))
        cmb = ttk.Combobox(row, values=list(self.PRESETS.keys()), state="readonly", textvariable=self.var_preset)
        cmb.pack(side=tk.LEFT, padx=(6, 8))
        cmb.bind("<<ComboboxSelected>>", self._apply_preset)

        self.var_scale = tk.IntVar(value=veg.get("scale", 50))
        self._slider("Noise Scale", 10, 300, 1, self.var_scale)

        self.var_oct = tk.IntVar(value=veg.get("octaves", 5))
        self._slider("Octaves", 1, 12, 1, self.var_oct)

        self.var_pers = tk.DoubleVar(value=veg.get("persistence", 0.55))
        self._slider("Persistence", 0.0, 1.0, 0.01, self.var_pers)

        self.var_lac = tk.DoubleVar(value=veg.get("lacunarity", 2.0))
        self._slider("Lacunarity", 1.0, 6.0, 0.1, self.var_lac)

        self.var_respect = tk.BooleanVar(value=veg.get("respect_terrain", True))
        cb = tk.Checkbutton(self, text="Respect terrain (no trees on water/asphalt)",
                            variable=self.var_respect, bg="#121212", fg="white",
                            selectcolor="#121212", command=self._write_back)
        cb.pack(anchor="w", padx=8, pady=(8, 2))

    def _slider(self, label, minv, maxv, step, var):
        row = tk.Frame(self, bg="#121212"); row.pack(fill=tk.X, padx=8, pady=(6, 0))
        _label(row, label).pack(anchor="w")
        inner = tk.Frame(row, bg="#121212"); inner.pack(fill=tk.X)
        s = tk.Scale(inner, from_=minv, to=maxv, resolution=step, showvalue=False,
                     orient=tk.HORIZONTAL, variable=var,
                     command=lambda _v: self._write_back(),
                     bg="#121212", fg="white", troughcolor="#555", highlightthickness=0)
        s.pack(side=tk.LEFT, fill=tk.X, expand=True)
        e = tk.Entry(inner, width=8)
        def sync(*_): e.delete(0, tk.END); e.insert(0, str(var.get()))
        var.trace_add("write", lambda *_: sync()); sync()
        e.bind("<Return>", lambda _e: self._apply_entry(e, var, minv, maxv))
        e.bind("<FocusOut>", lambda _e: self._apply_entry(e, var, minv, maxv))
        e.pack(side=tk.LEFT, padx=6)
        s.bind("<ButtonRelease-1>", lambda _e: self.on_click())

    def _apply_entry(self, e, var, mn, mx):
        try:
            v = float(e.get()); v = max(mn, min(mx, v))
            if isinstance(var.get(), int): v = int(round(v))
            var.set(v); self._write_back()
        except Exception: pass

    def _apply_preset(self, _e=None):
        self.conf.setdefault("vegetation", {})["preset"] = self.var_preset.get()
        P = self.PRESETS[self.var_preset.get()]
        self.conf["vegetation"].update(P)
        self.apply_conf(self.conf)
        self.on_change()

    def _write_back(self):
        veg = self.conf.setdefault("vegetation", {})
        veg.update({
            "scale": int(self.var_scale.get()),
            "octaves": int(self.var_oct.get()),
            "persistence": float(self.var_pers.get()),
            "lacunarity": float(self.var_lac.get()),
            "respect_terrain": bool(self.var_respect.get()),
        })
        self.on_change()

    def apply_conf(self, conf):
        self.conf = conf
        veg = conf.setdefault("vegetation", {})
        self.var_preset.set(veg.get("preset", "overgrown"))
        self.var_scale.set(veg.get("scale", 50))
        self.var_oct.set(veg.get("octaves", 5))
        self.var_pers.set(veg.get("persistence", 0.55))
        self.var_lac.set(veg.get("lacunarity", 2.0))
        self.var_respect.set(veg.get("respect_terrain", True))
