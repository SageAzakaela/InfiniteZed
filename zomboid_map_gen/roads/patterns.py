# zomboid_map_gen/roads/patterns.py
"""
Angle / layout helpers for roads.
"""

def snap_angle(angle: float, mode: str) -> float:
    mode = (mode or "free").lower()
    if mode == "ortho":
        return round(angle / 90.0) * 90 % 360
    if mode == "ortho45":
        return round(angle / 45.0) * 45 % 360
    # free
    return angle % 360
