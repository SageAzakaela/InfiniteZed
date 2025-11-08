# zomboid_map_gen/utils/seeds.py
"""
Seed helpers: derive deterministic per-layer seeds from a master seed.
"""

def derive_seed(master: int, name: str) -> int:
    """
    Create a stable integer seed from a master seed + name.
    """
    return (hash((master, name)) & 0xFFFFFFFF)
