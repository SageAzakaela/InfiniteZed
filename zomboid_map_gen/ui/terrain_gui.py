import tkinter as tk
from tkinter import ttk

def _label(p, t): return tk.Label(p, text=t, bg="#121212", fg="white")

class TerrainTab(tk.Frame):
    PRESETS = {
        "default":   dict(scale=60, octaves=6, persistence=0.50, lacunarity=2.0, water_threshold=0.25, dark_threshold=0.45, medium_threshold=0.70),
        "rural":     dict(scale=70, octaves=5, persistence=0.55, lacunarity=2.0, water_threshold=0.22, dark_threshold=0.44, medium_threshold=0.68),
        "suburban":  dict(scale=55, octaves=6, persistence=0.48, lacunarity=2.2, water_threshold=0.28, dark_threshold=0.46, medium_threshold=0.72),
        "overgrown": dict(scale=65, octaves=7, persistence=0.58, lacunarity=2.1, water_threshold=0.24, dark_threshold=0.43, medium_threshold=0.66),
    }

    def __init__(self, parent, conf, on_change, on_click):
        super().__init__(parent, bg="#121212")
        self.conf, self.on_change, self.on_click = conf, on_change, on_click
        ter = self.conf.setdefault("terrain", {})
        ter.setdefault("postprocess", {"edge_ragging": True, "speckle": True, "erosion": True})
        ter.setdefault("transform", {"rotation": 0, "offset_x": 0, "offset_y": 0})

        # Preset
        row = tk.Frame(self, bg="#121212"); row.pack(fill=tk.X, padx=8, pady=(8,4))
        _label(row, "Preset").pack(side=tk.LEFT)
        self.var_preset = tk.StringVar(value=ter.get("preset","default"))
        cmb = ttk.Combobox(row, values=list(self.PRESETS.keys()), state="readonly", textvariable=self.var_preset)
        cmb.pack(side=tk.LEFT, padx=(6,8))
        cmb.bind("<<ComboboxSelected>>", self._apply_preset)

        # Sliders
        self.var_scale = tk.IntVar(value=ter.get("scale",60));      self._slider("Noise Scale",      10,300,1,  self.var_scale)
        self.var_oct   = tk.IntVar(value=ter.get("octaves",6));     self._slider("Octaves",           1, 12,1,   self.var_oct)
        self.var_pers  = tk.DoubleVar(value=ter.get("persistence",0.5)); self._slider("Persistence", 0.0,1.0,0.01,self.var_pers)
        self.var_lac   = tk.DoubleVar(value=ter.get("lacunarity",2.0));  self._slider("Lacunarity",  1.0,6.0,0.1, self.var_lac)
        self.var_wth   = tk.DoubleVar(value=ter.get("water_threshold",0.25)); self._slider("Water Threshold",0.0,1.0,0.01,self.var_wth)
        self.var_dth   = tk.DoubleVar(value=ter.get("dark_threshold",0.45));  self._slider("Dark Threshold", 0.0,1.0,0.01,self.var_dth)
        self.var_mth   = tk.DoubleVar(value=ter.get("medium_threshold",0.70));self._slider("Medium Threshold",0.0,1.0,0.01,self.var_mth)

        # Post-processing
        _label(self,"Post-Processing").pack(anchor="w", padx=8, pady=(10,0))
        pp = ter["postprocess"]
        self.var_edge = tk.BooleanVar(value=pp.get("edge_ragging",True))
        self.var_speck= tk.BooleanVar(value=pp.get("speckle",True))
        self.var_eros = tk.BooleanVar(value=pp.get("erosion",True))
        for text, var in [("Edge Ragging",self.var_edge),("Speckle",self.var_speck),("Erosion",self.var_eros)]:
            cb = tk.Checkbutton(self, text=text, variable=var, bg="#121212", fg="white",
                                selectcolor="#121212", command=self._write_back)
            cb.pack(anchor="w", padx=14)

        # Transforms
        _label(self,"Transforms").pack(anchor="w", padx=8, pady=(10,0))
        tr = ter["transform"]
        self.var_rot  = tk.IntVar(value=tr.get("rotation",0));  self._slider("Rotation°", 0,359,1,self.var_rot)
        self.var_offx = tk.IntVar(value=tr.get("offset_x",0));  self._slider("Offset X", -2048,2048,1,self.var_offx)
        self.var_offy = tk.IntVar(value=tr.get("offset_y",0));  self._slider("Offset Y", -2048,2048,1,self.var_offy)

    def _slider(self, label, minv, maxv, step, var):
        row = tk.Frame(self, bg="#121212"); row.pack(fill=tk.X, padx=8, pady=(6,0))
        _label(row, label).pack(anchor="w")
        inner = tk.Frame(row, bg="#121212"); inner.pack(fill=tk.X)
        s = tk.Scale(inner, from_=minv, to=maxv, resolution=step, showvalue=False,
                     orient=tk.HORIZONTAL, variable=var,
                     command=lambda _v: self._write_back(),
                     bg="#121212", fg="white", troughcolor="#555", highlightthickness=0)
        s.pack(side=tk.LEFT, fill=tk.X, expand=True)
        e = tk.Entry(inner, width=8)
        def sync(*_): e.delete(0,tk.END); e.insert(0,str(var.get()))
        var.trace_add("write", lambda *_: sync()); sync()
        e.bind("<Return>", lambda _e: self._apply_entry(e,var,minv,maxv))
        e.bind("<FocusOut>", lambda _e: self._apply_entry(e,var,minv,maxv))
        e.pack(side=tk.LEFT, padx=6)
        s.bind("<ButtonRelease-1>", lambda _e: self.on_click())

    def _apply_entry(self, e, var, mn, mx):
        try:
            v = float(e.get()); v = max(mn, min(mx, v))
            if isinstance(var.get(), int): v = int(round(v))
            var.set(v); self._write_back()
        except Exception: pass

    def _apply_preset(self, _e=None):
        key = self.var_preset.get()
        self.conf.setdefault("terrain", {})["preset"] = key
        self.conf["terrain"].update(self.PRESETS[key])
        self.apply_conf(self.conf)
        self.on_change()

    def _write_back(self):
        ter = self.conf.setdefault("terrain", {})
        ter.update({
            "scale": int(self.var_scale.get()),
            "octaves": int(self.var_oct.get()),
            "persistence": float(self.var_pers.get()),
            "lacunarity": float(self.var_lac.get()),
            "water_threshold": float(self.var_wth.get()),
            "dark_threshold": float(self.var_dth.get()),
            "medium_threshold": float(self.var_mth.get()),
        })
        ter.setdefault("postprocess", {}).update({
            "edge_ragging": bool(self.var_edge.get()),
            "speckle": bool(self.var_speck.get()),
            "erosion": bool(self.var_eros.get()),
        })
        ter.setdefault("transform", {}).update({
            "rotation": int(self.var_rot.get()),
            "offset_x": int(self.var_offx.get()),
            "offset_y": int(self.var_offy.get()),
        })
        self.on_change()

    def apply_conf(self, conf):
        self.conf = conf
        ter = conf.setdefault("terrain", {})
        self.var_preset.set(ter.get("preset","default"))
        self.var_scale.set(ter.get("scale",60))
        self.var_oct.set(ter.get("octaves",6))
        self.var_pers.set(ter.get("persistence",0.5))
        self.var_lac.set(ter.get("lacunarity",2.0))
        self.var_wth.set(ter.get("water_threshold",0.25))
        self.var_dth.set(ter.get("dark_threshold",0.45))
        self.var_mth.set(ter.get("medium_threshold",0.70))
        pp = ter.setdefault("postprocess", {})
        self.var_edge.set(pp.get("edge_ragging",True))
        self.var_speck.set(pp.get("speckle",True))
        self.var_eros.set(pp.get("erosion",True))
        tr = ter.setdefault("transform", {})
        self.var_rot.set(tr.get("rotation",0))
        self.var_offx.set(tr.get("offset_x",0))
        self.var_offy.set(tr.get("offset_y",0))
