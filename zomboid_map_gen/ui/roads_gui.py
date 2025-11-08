import tkinter as tk
from tkinter import ttk

def _label(p, t): return tk.Label(p, text=t, bg="#121212", fg="white")

class RoadsTab(tk.Frame):
    def __init__(self, parent, conf, on_change, on_click):
        super().__init__(parent, bg="#121212")
        self.conf = conf
        self.on_change = on_change
        self.on_click = on_click
        roads = self.conf.setdefault("roads", {})

        _label(self, "Mode").pack(anchor="w", padx=8, pady=(8,0))
        self.var_mode = tk.StringVar(value=roads.get("mode", "ortho45"))
        cmb = ttk.Combobox(self, values=["ortho","diag45","ortho45","free"], state="readonly", textvariable=self.var_mode)
        cmb.pack(anchor="w", padx=8, pady=(0,8))
        cmb.bind("<<ComboboxSelected>>", lambda _e: self._write_back())

        # counts
        for label, key, default in [
            ("Highways", "num_highways", 2),
            ("Major Roads", "num_majors", 3),
            ("Main Roads", "num_mains", 6),
            ("Side Roads", "num_sides", 12),
        ]:
            row = tk.Frame(self, bg="#121212"); row.pack(anchor="w", padx=8, pady=(4,0))
            _label(row, label).pack(side=tk.LEFT)
            var = tk.IntVar(value=roads.get(key, default))
            sp = tk.Spinbox(row, from_=0, to=99, width=6, textvariable=var, command=self._write_back)
            sp.pack(side=tk.LEFT, padx=(6,0))
            setattr(self, f"var_{key}", var)

        rowb = tk.Frame(self, bg="#121212"); rowb.pack(fill=tk.X, padx=8, pady=(6,2))
        _label(rowb, "Branch Probability").pack(side=tk.LEFT)
        self.var_branch = tk.DoubleVar(value=roads.get("branch_prob", 0.15))
        spb = tk.Spinbox(rowb, from_=0.0, to=1.0, increment=0.01, width=8, textvariable=self.var_branch, command=self._write_back)
        spb.pack(side=tk.LEFT, padx=(6,12))

        _label(rowb, "Max Branch Depth").pack(side=tk.LEFT)
        self.var_depth = tk.IntVar(value=roads.get("max_branch_depth", 3))
        spd = tk.Spinbox(rowb, from_=0, to=12, width=6, textvariable=self.var_depth, command=self._write_back)
        spd.pack(side=tk.LEFT, padx=(6,12))

        rowp = tk.Frame(self, bg="#121212"); rowp.pack(fill=tk.X, padx=8, pady=(6,2))
        _label(rowp, "Pothole Density").pack(side=tk.LEFT)
        self.var_pothole = tk.DoubleVar(value=roads.get("pothole_density", 0.02))
        spp = tk.Spinbox(rowp, from_=0.0, to=0.5, increment=0.001, width=8, textvariable=self.var_pothole, command=self._write_back)
        spp.pack(side=tk.LEFT, padx=(6,12))

        self.var_ignore_water = tk.BooleanVar(value=roads.get("ignore_water", False))
        self.var_ignore_trees = tk.BooleanVar(value=roads.get("ignore_trees", False))
        for text, var in [("Ignore water", self.var_ignore_water), ("Ignore trees", self.var_ignore_trees)]:
            cb = tk.Checkbutton(self, text=text, variable=var, bg="#121212", fg="white",
                                selectcolor="#121212", command=self._write_back)
            cb.pack(anchor="w", padx=8)

    def _write_back(self):
        mode = self.var_mode.get()
        # TEMP: map 'free' to 'ortho45' until generator implements it
        effective_mode = "ortho45" if mode == "free" else mode

        r = self.conf.setdefault("roads", {})
        r.update({
            "mode": effective_mode,
            "num_highways": int(self.var_num_highways.get()),
            "num_majors": int(self.var_num_majors.get()),
            "num_mains": int(self.var_num_mains.get()),
            "num_sides": int(self.var_num_sides.get()),
            "branch_prob": float(self.var_branch.get()),
            "max_branch_depth": int(self.var_depth.get()),
            "pothole_density": float(self.var_pothole.get()),
            "ignore_water": bool(self.var_ignore_water.get()),
            "ignore_trees": bool(self.var_ignore_trees.get()),
        })
        self.on_change()

    def apply_conf(self, conf):
        self.conf = conf
        r = conf.setdefault("roads", {})
        self.var_mode.set(r.get("mode","ortho45"))
        self.var_num_highways.set(r.get("num_highways",2))
        self.var_num_majors.set(r.get("num_majors",3))
        self.var_num_mains.set(r.get("num_mains",6))
        self.var_num_sides.set(r.get("num_sides",12))
        self.var_branch.set(r.get("branch_prob",0.15))
        self.var_depth.set(r.get("max_branch_depth",3))
        self.var_pothole.set(r.get("pothole_density",0.02))
        self.var_ignore_water.set(r.get("ignore_water",False))
        self.var_ignore_trees.set(r.get("ignore_trees",False))
