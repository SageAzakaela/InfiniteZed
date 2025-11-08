# zomboid_map_gen/core.py
from pathlib import Path
from . import config as cfg
from .terrain import terrain_generator
from .vegetation import vegetation_generator
from .roads import road_generator
from .export import writer

def generate_from_config(conf: dict):
    out_dir = Path(conf.get("output_dir", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    terrain_img = terrain_generator.generate(conf) if conf.get("terrain", {}).get("enabled", True) else None
    veg_img = vegetation_generator.generate(conf, terrain_img) if conf.get("vegetation", {}).get("enabled", True) else None
    roads_img, lots_img = road_generator.generate(conf, terrain_img, veg_img) if conf.get("roads", {}).get("enabled", True) else (None, None)

    writer.save_all(conf, terrain_img, veg_img, roads_img, lots_img)
