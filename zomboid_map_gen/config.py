# zomboid_map_gen/config.py
import json
from pathlib import Path

def default_config() -> dict:
    return {
        "seed": 12345,
        "output_dir": "output",
        "canvas": {
            "cells_x": 1,
            "cells_y": 1,
            "cell_size": 300,
        },
        "terrain": {
            "enabled": True,
            "scale": 60,
            "octaves": 6,
            "persistence": 0.5,
            "lacunarity": 2.0,
            "water_threshold": 0.25,
            "dark_threshold": 0.45,
            "medium_threshold": 0.70,
            "preset": "default",
            "postprocess": {
                "edge_ragging": True,
                "speckle": True,
                "erosion": True,
                "strength": 0.6,
            },
        },
        "vegetation": {
            "enabled": True,
            "preset": "overgrown",
            "scale": 50,
            "octaves": 5,
            "persistence": 0.55,
            "lacunarity": 2.0,
            "respect_terrain": True,
        },
        "roads": {
            "enabled": True,
            "mode": "ortho45",
            "num_highways": 2,
            "num_majors": 3,
            "num_mains": 6,
            "num_sides": 12,
            "branch_prob": 0.15,
            "max_branch_depth": 3,
            "pothole_density": 0.02,
            "ignore_water": False,
            "ignore_trees": False,
        },
        "export": {
            "terrain_png": "terrain.png",
            "vegetation_png": "vegetation.png",
            "roads_png": "roads.png",
            "combined_png": "combined.png",
            "lots_png": "lots.png",
        },
    }

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(conf: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)
