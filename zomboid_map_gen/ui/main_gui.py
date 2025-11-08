import os, sys, json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from .. import core, config as cfg
from .sound import SoundPlayer
from .terrain_gui import TerrainTab
from .vegetation_gui import VegetationTab
from .roads_gui import RoadsTab
from .export_gui import ExportTab


THUMB_SIZE = (300, 300)   # larger thumbnails, keep aspect via .thumbnail


class ZedInfiniMapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zed InfiniMapper")
        self.configure(bg="#121212")
        self.geometry("1360x760")

        # project root (…/zomboid_map_gen/..)
        self.project_root = Path(__file__).resolve().parents[2]
        self.sound = SoundPlayer(self.project_root)

        # config in memory
        self.conf = cfg.default_config()

        # debounce / busy
        self._regen_after_id = None
        self._regen_delay_ms = 250
        self._busy = False

        # thumbnail image refs (prevent GC)
        self._thumb_imgs = {"terrain": None, "vegetation": None, "combo": None, "roads": None}

        self._build_ui()
        self._schedule_regen()

    # ---------- UI ----------
    def _build_ui(self):
        self._build_menu()

        # Top bar
        top = tk.Frame(self, bg="#121212")
        top.pack(side=tk.TOP, fill=tk.X)
        self.var_live = tk.BooleanVar(value=True)
        live = tk.Checkbutton(top, text="Live Update", variable=self.var_live, bg="#121212", fg="white",
                              selectcolor="#121212", command=self._click)
        live.pack(side=tk.LEFT, padx=10, pady=6)

        gen = tk.Button(top, text="Generate", command=self._generate_clicked, bg="#2f2f2f", fg="white", padx=16, pady=6)
        gen.pack(side=tk.RIGHT, padx=10, pady=6)

        # Body split: left tabs, right thumbnails
        body = tk.Frame(self, bg="#121212")
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg="#121212")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.nb = ttk.Notebook(left)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 0))
        self._style_notebook()

        # Tabs (each is passed callbacks to update config and schedule regen)
        self.terrain_tab = TerrainTab(self.nb, self.conf, on_change=self.on_params_changed, on_click=self._click)
        self.nb.add(self.terrain_tab, text="Terrain")

        self.vegetation_tab = VegetationTab(self.nb, self.conf, on_change=self.on_params_changed, on_click=self._click)
        self.nb.add(self.vegetation_tab, text="Vegetation")

        self.roads_tab = RoadsTab(self.nb, self.conf, on_change=self.on_params_changed, on_click=self._click)
        self.nb.add(self.roads_tab, text="Roads")

        self.export_tab = ExportTab(self.nb, self.conf, on_change=self.on_params_changed, on_click=self._click)
        self.nb.add(self.export_tab, text="Export")

        # Right: thumbnails only (no big preview)
        right = tk.Frame(body, bg="#121212", width=620)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        self._thumb_grid = tk.Frame(right, bg="#121212")
        self._thumb_grid.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._thumb_labels = {}
        self._thumb_labels["terrain"] = self._make_thumb_box(self._thumb_grid, "Terrain", 0)
        self._thumb_labels["vegetation"] = self._make_thumb_box(self._thumb_grid, "Vegetation", 1)
        self._thumb_labels["combo"] = self._make_thumb_box(self._thumb_grid, "Terrain + Roads", 2)
        self._thumb_labels["roads"] = self._make_thumb_box(self._thumb_grid, "Road Network", 3)

        # Status
        self.status_var = tk.StringVar(value="Ready.")
        status = tk.Label(self, textvariable=self.status_var, bg="#121212", fg="white", anchor="w")
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_menu(self):
        mb = tk.Menu(self)
        filem = tk.Menu(mb, tearoff=0)
        filem.add_command(label="Open Config…", command=self._menu_load)
        filem.add_command(label="Save Config As…", command=self._menu_save)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.destroy)
        mb.add_cascade(label="File", menu=filem)

        exportm = tk.Menu(mb, tearoff=0)
        exportm.add_command(label="Open Output Folder", command=self._open_output_folder)
        mb.add_cascade(label="Export", menu=exportm)

        helpm = tk.Menu(mb, tearoff=0)
        helpm.add_command(label="About", command=lambda: messagebox.showinfo("About", "Zed InfiniMapper"))
        mb.add_cascade(label="Help", menu=helpm)

        self.config(menu=mb)

    def _style_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#121212", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e1e1e", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#333333")])

    def _make_thumb_box(self, parent, title, col):
        wrap = tk.Frame(parent, bg="#121212")
        wrap.grid(row=0, column=col, padx=8, pady=8, sticky="n")

        tk.Label(wrap, text=title, bg="#121212", fg="white").pack(anchor="w")
        lbl = tk.Label(wrap, bg="#1b1b1b", width=THUMB_SIZE[0], height=THUMB_SIZE[1])
        lbl.pack()
        lbl.bind("<Double-Button-1>", lambda e, key=title: self._open_single_image(key))
        return lbl

    # ---------- Events / sounds ----------
    def _click(self):
        self.sound.click()

    def _menu_save(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        cfg.save_config(self.conf, path)
        self.status_var.set(f"Config saved: {path}")
        self.sound.bubble()

    def _menu_load(self):
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.conf = cfg.load_config(path)
        # push into tabs
        self.terrain_tab.apply_conf(self.conf)
        self.vegetation_tab.apply_conf(self.conf)
        self.roads_tab.apply_conf(self.conf)
        self.export_tab.apply_conf(self.conf)
        self.status_var.set(f"Config loaded: {path}")
        self.sound.bubble()
        self._schedule_regen()

    def _open_output_folder(self):
        out_dir = Path(self.conf.get("output_dir", "output")).resolve()
        try:
            if sys.platform.startswith("win"): os.startfile(str(out_dir))
            elif sys.platform == "darwin": os.system(f'open "{out_dir}"')
            else: os.system(f'xdg-open "{out_dir}"')
        except Exception: pass
        self._click()

    def _open_single_image(self, key_title):
        # map from display title to actual file path
        t_path, v_path, r_path, c_path = self._paths()
        mapping = {
            "Terrain": t_path,
            "Vegetation": v_path,
            "Terrain + Roads": c_path,  # combined
            "Road Network": r_path,
        }
        p = mapping.get(key_title)
        if not p or not p.exists(): return
        try:
            if sys.platform.startswith("win"): os.startfile(str(p))
            elif sys.platform == "darwin": os.system(f'open "{p}"')
            else: os.system(f'xdg-open "{p}"')
        except Exception: pass

    # ---------- Change / regen ----------
    def on_params_changed(self, *_):
        # tabs already wrote values into self.conf
        if self.var_live.get():
            self._schedule_regen()

    def _schedule_regen(self):
        if self._regen_after_id:
            self.after_cancel(self._regen_after_id)
        self._regen_after_id = self.after(self._regen_delay_ms, self._do_regen)

    def _do_regen(self):
        self._regen_after_id = None
        if self._busy: return
        try:
            self._busy = True
            self.status_var.set("Generating…")
            self.update_idletasks()
            core.generate_from_config(self.conf)
            self._update_thumbs()
            self.status_var.set("Live update complete.")
        except Exception as e:
            self.status_var.set("Generation failed.")
            self.sound.oops()
            messagebox.showerror("Error", f"{e}")
        finally:
            self._busy = False

    def _generate_clicked(self):
        try:
            self.status_var.set("Generating…")
            self.update_idletasks()
            core.generate_from_config(self.conf)
            self._update_thumbs()
            self.status_var.set("Generation complete.")
            self.sound.tada()
        except Exception as e:
            self.status_var.set("Generation failed.")
            self.sound.oops()
            messagebox.showerror("Error", f"{e}")

    # ---------- Thumbnails ----------
    def _paths(self):
        out_dir = Path(self.conf.get("output_dir","output"))
        exp = self.conf.get("export", {})
        # respect config but fall back smartly
        t = out_dir / exp.get("terrain_png", "terrain.png")
        v = out_dir / exp.get("vegetation_png", "vegetation.png")
        r = out_dir / exp.get("roads_png", "roads.png")

        # combined might be preview.png or combined.png depending on writer/UI
        c = out_dir / exp.get("combined_png", "preview.png")
        if not c.exists():
            alt = self._pick_latest(out_dir, [exp.get("combined_png",""), "preview.png", "combined.png"])
            c = alt if alt else c
        return t, v, r, c


    def _set_thumb(self, key, path: Path):
        if not path or not path.exists():
            self._thumb_labels[key].configure(image="")
            self._thumb_imgs[key] = None
            return
        img = self._open_image_fresh(path)
        img.thumbnail(THUMB_SIZE, Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self._thumb_labels[key].configure(image=imgtk)
        self._thumb_imgs[key] = imgtk

    def _update_thumbs(self):
        t_path, v_path, r_path, c_path = self._paths()

        self._set_thumb("terrain", t_path)
        self._set_thumb("vegetation", v_path)

        if c_path and c_path.exists():
            self._set_thumb("combo", c_path)
        else:
            # build combo from terrain+roads if writer didn’t emit combined
            if t_path.exists():
                img = self._open_image_fresh(t_path).convert("RGBA")
                if r_path.exists():
                    roads = self._open_image_fresh(r_path).convert("RGBA")
                    img.alpha_composite(roads)
                img.thumbnail(THUMB_SIZE, Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self._thumb_labels["combo"].configure(image=imgtk)
                self._thumb_imgs["combo"] = imgtk
            else:
                self._thumb_labels["combo"].configure(image="")
                self._thumb_imgs["combo"] = None

        self._set_thumb("roads", r_path)


    def _open_image_fresh(self, path: Path) -> Image.Image:
        # avoid stale handles/caching
        with Image.open(path) as im:
            im.load()
            return im.copy()

    def _pick_latest(self, out_dir: Path, candidates: list[str]) -> Path | None:
        latest = None; lm = -1
        for name in candidates:
            p = out_dir / name
            if p.exists():
                m = p.stat().st_mtime
                if m > lm: latest, lm = p, m
        return latest



def main():
    app = ZedInfiniMapperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
