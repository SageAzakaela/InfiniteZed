# zomboid_map_gen/vegetation/vegetation_generator.py
"""
Vegetation renderer.

- generates a vegetation.png-style mask using the user's veg color scheme
- uses noise to decide which vegetation band to use
- can optionally respect terrain (no trees on water or asphalt)
"""

from PIL import Image
from ..utils import noise_utils, colors as base_colors
from . import presets


# ordered list of vegetation colors from lowest → highest density
# (we'll map noise 0..1 into this list)
VEG_BANDS = [
    base_colors.VEG["none"][:3],               # 0
    base_colors.VEG["grass_some_trees"][:3],   # 1
    base_colors.VEG["light_long_grass"][:3],   # 2
    base_colors.VEG["trees_grass"][:3],        # 3
    base_colors.VEG["dense_trees_grass"][:3],  # 4
    base_colors.VEG["dense_forest"][:3],       # 5
    base_colors.VEG["bushes_grass"][:3],       # 6
    # you also have dead corn colors — we can optionally sprinkle these later
]


# terrain colors we SHOULD NOT overwrite with vegetation if respect_terrain=True
TERRAIN_BLOCKLIST = {
    base_colors.VANILLA["water"][:3],
    base_colors.VANILLA["light_asphalt"][:3],
    base_colors.VANILLA["dark_asphalt"][:3],
    base_colors.VANILLA["medium_asphalt"][:3],
}


def _get_canvas_size(conf: dict) -> tuple[int, int]:
    canvas_conf = conf.get("canvas", {})
    cell_size = canvas_conf.get("cell_size", 300)
    cells_x = canvas_conf.get("cells_x", 1)
    cells_y = canvas_conf.get("cells_y", 1)
    width = cell_size * cells_x
    height = cell_size * cells_y
    return width, height


def _terrain_pixel_blocked(terrain_img, x, y, respect: bool) -> bool:
    if not respect:
        return False
    if terrain_img is None:
        return False
    rgb = terrain_img.getpixel((x, y))[:3]
    return rgb in TERRAIN_BLOCKLIST


def generate(conf: dict, terrain_img=None):
    veg_conf = conf.get("vegetation", {})
    preset_vals = presets.get_preset(veg_conf.get("preset", "overgrown"))

    width, height = _get_canvas_size(conf)

    seed = conf.get("seed", 0) + 999  # shift so veg != terrain
    scale = veg_conf.get("scale", preset_vals["scale"])
    octaves = veg_conf.get("octaves", preset_vals["octaves"])
    persistence = veg_conf.get("persistence", preset_vals["persistence"])
    lacunarity = veg_conf.get("lacunarity", preset_vals["lacunarity"])
    respect_terrain = veg_conf.get("respect_terrain", True)

    img = Image.new("RGBA", (width, height))
    px = img.load()

    # we can normalize as we go — don't need to store whole array, since noise fallback already ~[-1,1]
    # but to make it consistent, we'll gather first
    vals = []
    for x in range(width):
        for y in range(height):
            v = noise_utils.perlin2(
                x,
                y,
                scale=scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                seed=seed,
            )
            vals.append(v)

    vmin = min(vals)
    vmax = max(vals)
    vrange = vmax - vmin if vmax != vmin else 1.0
    bands_count = len(VEG_BANDS)

    i = 0
    for x in range(width):
        for y in range(height):
            # optional terrain-aware rule
            if _terrain_pixel_blocked(terrain_img, x, y, respect_terrain):
                # keep terrain as-is, but vegetation map wants "none" (black)
                px[x, y] = base_colors.VEG["none"]
                i += 1
                continue

            v = (vals[i] - vmin) / vrange  # 0..1
            i += 1
            idx = int(v * bands_count)
            if idx >= bands_count:
                idx = bands_count - 1

            col = VEG_BANDS[idx]
            px[x, y] = col + (255,)

    return img
