# zomboid_map_gen/utils/noise_utils.py
import random

try:
    import noise  # optional: pip install noise
except ImportError:
    noise = None


def perlin2(
    x: float,
    y: float,
    scale: float = 60.0,
    octaves: int = 4,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    seed: int = 0,
) -> float:
    """
    Returns a value in roughly [-1, 1].
    If the 'noise' library is available, we use real Perlin.
    Otherwise we use a deterministic PRNG-based fallback so generation still runs.
    """
    if noise is None:
        # deterministic pseudo-noise
        key = (int(x) * 928371 + int(y) * 1237 + int(seed) * 19349663) & 0xFFFFFFFF
        rnd = random.Random(key)
        return rnd.random() * 2 - 1

    return noise.pnoise2(
        x / scale,
        y / scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        base=seed % 1024,
    )
