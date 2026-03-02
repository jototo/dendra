"""Fractal noise — organic irregularity for trunk and crown edges.

Uses the `noise` library for Perlin noise (smooth, continuous randomness
that looks natural rather than purely random). Applied to:
  - Trunk segment endpoints (slight lateral drift)
  - Crown silhouette control points
"""

from __future__ import annotations

import math

try:
    from noise import pnoise1, pnoise2
    _NOISE_AVAILABLE = True
except ImportError:
    _NOISE_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fallback: value noise if `noise` library is unavailable
# ---------------------------------------------------------------------------

def _value_noise_1d(x: float, seed: int = 0) -> float:
    """Simple pseudo-random smooth noise fallback."""
    xi = int(math.floor(x))
    xf = x - xi

    def _rand(n: int) -> float:
        n = (n + seed * 7919) & 0xFFFFFFFF
        n = ((n >> 16) ^ n) * 0x45D9F3B & 0xFFFFFFFF
        n = ((n >> 16) ^ n) * 0x45D9F3B & 0xFFFFFFFF
        n = (n >> 16) ^ n
        return (n & 0x7FFFFFFF) / 0x7FFFFFFF * 2.0 - 1.0

    a, b = _rand(xi), _rand(xi + 1)
    t = xf * xf * (3 - 2 * xf)   # smoothstep
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def perlin1d(x: float, octaves: int = 4, persistence: float = 0.5, seed: int = 0) -> float:
    """Fractal (octave-summed) 1-D Perlin noise in [-1, 1].

    Falls back to value noise if the `noise` library isn't installed.
    """
    if _NOISE_AVAILABLE:
        return pnoise1(x + seed * 0.1, octaves=octaves, persistence=persistence)
    # Fallback: sum octaves manually
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_val = 0.0
    for _ in range(octaves):
        value += _value_noise_1d(x * frequency, seed) * amplitude
        max_val += amplitude
        amplitude *= persistence
        frequency *= 2.0
    return value / max_val if max_val else 0.0


def perlin2d(
    x: float,
    y: float,
    octaves: int = 4,
    persistence: float = 0.5,
    seed: int = 0,
) -> float:
    """Fractal 2-D Perlin noise in [-1, 1]."""
    if _NOISE_AVAILABLE:
        return pnoise2(x + seed * 0.1, y + seed * 0.1, octaves=octaves, persistence=persistence)
    # Fallback: use 1d noise on diagonal
    return perlin1d(x * 1.3 + y * 0.7, octaves=octaves, persistence=persistence, seed=seed)


def drift_point(
    x: float,
    y: float,
    t: float,
    amplitude: float = 3.0,
    octaves: int = 3,
    seed: int = 0,
) -> tuple[float, float]:
    """Apply Perlin drift to a point — used for organic trunk/branch wobble.

    `t` is a parameter along the branch (0→1). Amplitude is in SVG units.
    """
    dx = perlin1d(t * 2.0, octaves=octaves, seed=seed) * amplitude
    dy = perlin1d(t * 2.0 + 100.0, octaves=octaves, seed=seed + 1) * amplitude
    return x + dx, y + dy


def crown_noise_radii(
    n_points: int,
    base_radius: float,
    roughness: float = 0.15,
    octaves: int = 5,
    seed: int = 0,
) -> list[float]:
    """Generate noisy radii around a crown silhouette.

    Returns `n_points` radius values that vary organically around base_radius.
    roughness=0 → perfect circle; roughness=1 → very jagged.
    """
    radii = []
    for i in range(n_points):
        t = i / n_points
        noise_val = perlin1d(t * 3.0, octaves=octaves, seed=seed)
        radii.append(base_radius * (1.0 + roughness * noise_val))
    return radii
