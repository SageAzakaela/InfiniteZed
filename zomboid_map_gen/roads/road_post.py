# zomboid_map_gen/roads/road_post.py
"""
Post-process passes for roads:
- potholes (jagged, density-based)
- later: parking, mask carving
"""

import random
from PIL import Image, ImageDraw
from ..utils import colors as base_colors

# road-ish colors we allow potholes on
ASPHALTS = {
    base_colors.VANILLA["dark_asphalt"][:3],
    base_colors.VANILLA["medium_asphalt"][:3],
    base_colors.VANILLA["light_asphalt"][:3],
}

# road-ish colors we DO NOT pothole
DIRTLIKE = {
    base_colors.VANILLA["dirt"][:3],
    base_colors.VANILLA["gravel_dirt"][:3],
    base_colors.VANILLA["sand"][:3],
}

DARK_POTHOLE = base_colors.VANILLA["dark_pothole"][:3]
LIGHT_POTHOLE = base_colors.VANILLA["light_pothole"][:3]


def apply_potholes_noise_jagged(road_img: Image.Image, density=0.02, seed=None):
    """
    Place small jagged shapes on asphalt areas, using asphalt brightness to pick
    light vs dark pothole. Skip dirt / gravel roads.
    """
    if density <= 0:
        return road_img

    w, h = road_img.size
    d = ImageDraw.Draw(road_img)
    rnd = random.Random(seed) if seed is not None else random

    num_attempts = int(w * h * density * 0.15)

    for _ in range(num_attempts):
        x = rnd.randint(0, w - 1)
        y = rnd.randint(0, h - 1)
        px = road_img.getpixel((x, y))
        base = px[:3]

        # only on asphalt
        if base not in ASPHALTS:
            continue

        # choose pothole color based on which asphalt it is
        if base == base_colors.VANILLA["dark_asphalt"][:3] or base == base_colors.VANILLA["medium_asphalt"][:3]:
            pothole_col = DARK_POTHOLE
        else:
            pothole_col = LIGHT_POTHOLE

        # jagged polygon around (x,y)
        points = []
        radius = rnd.randint(2, 4)
        for _ in range(rnd.randint(4, 7)):
            ox = x + rnd.randint(-radius, radius)
            oy = y + rnd.randint(-radius, radius)
            points.append((ox, oy))

        d.polygon(points, fill=pothole_col + (255,))

    return road_img


def add_parking_lot_rect(lots_img: Image.Image, x, y, w, h, color=(255, 0, 0, 255)):
    d = ImageDraw.Draw(lots_img)
    d.rectangle([x, y, x + w, y + h], fill=color)
