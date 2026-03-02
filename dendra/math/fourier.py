"""Fourier crown envelope — silhouette shaping for canopy-dominant trees.

For species like White Oak and Sycamore whose silhouette is defined by
a smooth outer canopy shape, we build an envelope using a Fourier series.
The crown is described as a polar curve: r(θ) = Σ aₙcos(nθ) + bₙsin(nθ).

This lets us parameterize the exact "personality" of each crown:
  - White Oak: wide, symmetric dome (low-frequency terms dominate)
  - Sycamore: asymmetric, tall spread (odd harmonics, slight DC offset)
  - Dogwood: tiered horizontal lobes (specific harmonic ratios)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class FourierCrown:
    """Fourier series description of a tree crown envelope.

    a_coeffs[n] and b_coeffs[n] are the cosine/sine amplitudes for harmonic n.
    Index 0 is the DC (mean radius) term.
    """
    a_coeffs: list[float]           # cosine terms
    b_coeffs: list[float]           # sine terms
    cx: float = 0.0                 # crown centre x offset from trunk top
    cy: float = 0.0                 # crown centre y offset from trunk top
    scale: float = 1.0              # overall radius scale


def evaluate(crown: FourierCrown, theta: float) -> float:
    """Evaluate crown radius at angle theta (radians)."""
    r = 0.0
    for n, (a, b) in enumerate(zip(crown.a_coeffs, crown.b_coeffs)):
        r += a * math.cos(n * theta) + b * math.sin(n * theta)
    return max(0.0, r * crown.scale)


def crown_polygon(
    crown: FourierCrown,
    n_points: int = 128,
    noise_fn=None,
    noise_amplitude: float = 0.0,
    seed: int = 0,
) -> list[tuple[float, float]]:
    """Sample the Fourier crown into an (x, y) polygon centred at (cx, cy).

    Optionally applies organic noise to each radius via noise_fn(t, seed) → [-1,1].
    """
    points = []
    for i in range(n_points):
        theta = 2 * math.pi * i / n_points
        r = evaluate(crown, theta)
        if noise_fn is not None and noise_amplitude > 0:
            t = i / n_points
            r += noise_amplitude * r * noise_fn(t * 4.0, seed=seed)
        x = crown.cx + r * math.cos(theta)
        y = crown.cy + r * math.sin(theta)
        points.append((x, y))
    return points


# ---------------------------------------------------------------------------
# Species crown presets
# ---------------------------------------------------------------------------

def dome_crown(radius: float, asymmetry: float = 0.0, flatten: float = 0.0) -> FourierCrown:
    """Broad dome — White Oak style.

    asymmetry: slight lean (0 = symmetric)
    flatten: compress top (0 = full dome, positive = flatter top)
    """
    return FourierCrown(
        a_coeffs=[radius, 0.0, radius * flatten * 0.4, 0.0],
        b_coeffs=[0.0, asymmetry * radius * 0.25, 0.0, 0.0],
    )


def tiered_crown(radius: float, n_tiers: int = 3, tier_depth: float = 0.25) -> FourierCrown:
    """Horizontal-tiered crown — Dogwood style.

    Creates lobes at n_tiers angular positions via specific harmonics.
    """
    a = [radius, 0.0]
    b = [0.0, 0.0]
    # Add harmonic at n_tiers frequency for lobing
    for _ in range(n_tiers - 1):
        a.append(0.0)
        b.append(0.0)
    a.append(-tier_depth * radius)
    b.append(0.0)
    return FourierCrown(a_coeffs=a, b_coeffs=b)


def columnar_crown(radius: float, height_ratio: float = 2.5) -> FourierCrown:
    """Tall narrow crown — Cedar style.

    Uses a vertical ellipse in polar form: r(θ) = R - C·cos(2θ)
      - θ=0   (sides):  r = R - C  → narrow
      - θ=π/2 (top):    r = R + C  → tall

    C is derived so that height/width = height_ratio.
    """
    # C = R * (height_ratio - 1) / (height_ratio + 1)
    C = radius * (height_ratio - 1) / (height_ratio + 1)
    return FourierCrown(
        a_coeffs=[radius, 0.0, -C],
        b_coeffs=[0.0, 0.0, 0.0],
    )


def vase_crown(radius: float, spread: float = 1.3) -> FourierCrown:
    """Spreading vase — Redbud style.

    Wide at top, narrower at the join to trunk.
    """
    return FourierCrown(
        a_coeffs=[radius, 0.0, radius * 0.2, 0.0],
        b_coeffs=[0.0, 0.0, 0.0, radius * 0.05],
        scale=spread,
        cy=radius * 0.1,
    )
