# zomboid_map_gen/export/writer.py
from pathlib import Path

def save_all(conf, terrain_img, veg_img, roads_img, lots_img):
    out_dir = Path(conf.get("output_dir", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    if terrain_img:
        terrain_img.save(out_dir / "terrain.png")
    if veg_img:
        veg_img.save(out_dir / "vegetation.png")
    if roads_img:
        roads_img.save(out_dir / "roads.png")

    if terrain_img:
        combo = terrain_img.copy()
        if veg_img:
            combo.alpha_composite(veg_img)
        if roads_img:
            combo.alpha_composite(roads_img)
        combo.save(out_dir / "preview.png")
