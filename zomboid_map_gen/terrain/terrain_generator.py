# zomboid_map_gen/terrain/terrain_generator.py
"""
Terrain generator.

Features:
- uses canvas size from config
- supports either:
  (a) thresholds in config["terrain"]  (simple mode)
  (b) explicit layer list in config["terrain"]["layers"] (layer mode)
- uses per-layer noise from utils.noise_utils
- applies postprocess passes at the end
"""

from PIL import Image, ImageChops

from ..utils import noise_utils, colors as base_colors, seeds as seed_utils
from . import presets, postprocess


def _get_canvas_size(conf: dict) -> tuple[int, int]:
    canvas_conf = conf.get("canvas", {})
    cell_size = canvas_conf.get("cell_size", 300)
    cells_x = canvas_conf.get("cells_x", 1)
    cells_y = canvas_conf.get("cells_y", 1)
    width = cell_size * cells_x
    height = cell_size * cells_y
    return width, height


def _generate_simple(conf: dict, width: int, height: int) -> Image.Image:
    """
    Older/simple style: single noise field + thresholds.
    Good for testing when you don't want to define all layers.
    """
    terrain_conf = conf.get("terrain", {})
    seed = conf.get("seed", 0)

    preset_name = terrain_conf.get("preset", "default")
    preset_vals = presets.get_preset(preset_name)

    scale = terrain_conf.get("scale", preset_vals["scale"])
    octaves = terrain_conf.get("octaves", 6)
    persistence = terrain_conf.get("persistence", 0.5)
    lacunarity = terrain_conf.get("lacunarity", 2.0)

    water_th = terrain_conf.get("water_threshold", preset_vals["water_threshold"])
    dark_th = terrain_conf.get("dark_threshold", preset_vals["dark_threshold"])
    med_th = terrain_conf.get("medium_threshold", preset_vals["medium_threshold"])

    # grab vanilla-ish colors
    water = base_colors.VANILLA["water"][:3]
    dark_grass = base_colors.VANILLA["dark_grass"][:3]
    med_grass = base_colors.VANILLA["med_grass"][:3]
    light_grass = base_colors.VANILLA["light_grass"][:3]
    dirt = base_colors.VANILLA["dirt"][:3]
    sand = base_colors.VANILLA["sand"][:3]

    img = Image.new("RGB", (width, height))

    # collect noise first so we can normalize to 0..1
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

    i = 0
    for x in range(width):
        for y in range(height):
            v = (vals[i] - vmin) / vrange
            i += 1

            if v < water_th:
                c = water
            elif v < dark_th:
                c = dark_grass
            elif v < med_th:
                c = med_grass
            elif v < min(1.0, med_th + 0.10):
                c = light_grass
            elif v < min(1.0, med_th + 0.18):
                c = dirt
            else:
                c = sand

            img.putpixel((x, y), c)

    return img.convert("RGBA")


def _generate_layers(conf: dict, width: int, height: int) -> Image.Image:
    """
    Newer/layered style:
    terrain: {
        "layers": [
            {"name": "water", "color": [0,138,255,255], "scale": 60, "octaves": 5, "threshold": 0.3},
            {"name": "dark_grass", ...},
            ...
        ]
    }

    We paint in order: first layer = lowest priority, last = top.
    """
    terrain_conf = conf.get("terrain", {})
    master_seed = conf.get("seed", 0)
    layers = terrain_conf.get("layers", [])

    # if no layers provided, fall back to simple
    if not layers:
        return _generate_simple(conf, width, height)

    # precompute per-layer noise arrays
    layer_noises: list[list[float]] = []
    vmins = []
    vmaxs = []

    for layer in layers:
        scale = layer.get("scale", 60)
        octaves = layer.get("octaves", 5)
        persistence = layer.get("persistence", 0.5)
        lacunarity = layer.get("lacunarity", 2.0)
        layer_seed = layer.get("seed")
        if layer_seed is None:
            layer_seed = seed_utils.derive_seed(master_seed, layer.get("name", "layer"))

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
                    seed=layer_seed,
                )
                vals.append(v)
        vmin = min(vals)
        vmax = max(vals)
        layer_noises.append(vals)
        vmins.append(vmin)
        vmaxs.append(vmax)

    # now actually paint
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # We'll keep a separate coverage mask if later we want "linked thresholds"
    for li, layer in enumerate(layers):
        color = tuple(layer.get("color", (255, 0, 255, 255)))
        threshold = float(layer.get("threshold", 0.5))
        vals = layer_noises[li]
        vmin = vmins[li]
        vmax = vmaxs[li]
        vrange = vmax - vmin if vmax != vmin else 1.0

        i = 0
        for x in range(width):
            for y in range(height):
                v = (vals[i] - vmin) / vrange
                i += 1
                if v >= threshold:
                    img.putpixel((x, y), color)

    return img

def _apply_transform(img: Image.Image, conf: dict) -> Image.Image:
    tr = conf.get("terrain", {}).get("transform", {})
    rot = int(tr.get("rotation", 0)) % 360
    offx = int(tr.get("offset_x", 0))
    offy = int(tr.get("offset_y", 0))

    if rot:
        # keep canvas size; NEAREST to preserve palette edges
        img = img.rotate(-rot, resample=Image.NEAREST, expand=False)
    if offx or offy:
        img = ImageChops.offset(img, offx, offy)
    return img


def generate(conf: dict):


    width, height = _get_canvas_size(conf)
    terrain_conf = conf.get("terrain", {})

    # choose path: if user gave layers, use layered version, otherwise simple
    if terrain_conf.get("layers"):
        img = _generate_layers(conf, width, height)
    else:
        img = _generate_simple(conf, width, height)

    # postprocess (erosion, speckle, edge rag)
    img = postprocess.apply_all(img, conf)
    img = _apply_transform(img, conf)
    return img

