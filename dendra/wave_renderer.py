"""Wave renderer — draws tree silhouettes as vertical waveform envelopes.

Instead of L-system geometry, the tree is rendered as a filled polygon whose
left and right edges are traced by the harmonic wave sum sampled upward along
the tree height. Rotating the audio waveform 90° produces a silhouette that
combines the mathematical wave character of the species' note with an organic
tree shape.

Each species looks distinct:
  - The note frequency determines how many wave cycles are visible (density)
  - The harmonic decay determines edge roughness (complex vs smooth texture)
  - The angle_scale determines how strongly the wave modulates the width
  - Perlin noise adds independent left/right asymmetry for organic irregularity
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

from dendra.math.wave import note_to_freq, harmonic_weights
from dendra.math.fractal import perlin1d
from dendra.color import ColorConfig, resolve_fill, trunk_fill
from dendra.species.base import TreeSpec


def render_waveform(
    spec: TreeSpec,
    color: ColorConfig,
    note: str | None = None,
    harmonic_depth: int | None = None,
    seed: int = 0,
    canvas_width: int = 600,
    canvas_height: int = 700,
) -> ET.Element:
    """Render tree as a vertical waveform silhouette.

    Returns the root <svg> Element.
    """
    note_str = note or spec.default_note
    freq = note_to_freq(note_str)
    n_harm = harmonic_depth if harmonic_depth is not None else spec.wave.n_harmonics
    weights = harmonic_weights(n_harm, spec.wave.harmonic_decay)
    seed_f = float(seed) * 0.137

    # Number of wave cycles visible over the crown height.
    # Proportional to log(freq) so higher notes produce denser texture.
    n_cycles = max(8, int(math.log2(max(freq, 20)) * 2.5))

    # Crown geometry
    # Waveform style uses a taller trunk than lsystem style — crown sits higher.
    wave_trunk_ratio = min(spec.crown.trunk_height_ratio + 0.30, 0.60)
    trunk_px = canvas_height * wave_trunk_ratio
    crown_y_bottom = canvas_height - trunk_px
    crown_y_top = canvas_height * 0.07
    crown_height = crown_y_bottom - crown_y_top
    cx = canvas_width / 2

    # Width scales with trunk_width_base (proxy for crown breadth per species).
    # Normalized to 16 (sycamore, widest) so narrow species like pine are thinner.
    width_factor = spec.trunk_width_base / 16.0
    max_hw = canvas_width * 0.22 * width_factor
    clamp_hw = canvas_width / 2 - 8  # hard clamp — never reach canvas edge

    # Texture amplitude: maps angle_scale to how strongly the wave modulates width.
    wave_scale = spec.wave.angle_scale / 45.0 * 0.55

    # Color
    canopy_fill, grad_el = resolve_fill(color, "waveGradient")
    branch_fill_color = trunk_fill(color)

    # --- Envelope function ---
    # t=0 = crown top (tips), t=1 = crown bottom (base)
    # Widest around t=0.55, tapers smoothly to 0 at both ends.
    def envelope(t: float) -> float:
        return (t ** 0.55) * ((1.0 - t) ** 0.55) * 4.0

    # --- Sample waveform ---
    n_samples = 600
    left_pts: list[tuple[float, float]] = []
    right_pts: list[tuple[float, float]] = []

    w_sum = sum(weights[1:]) or 1.0

    for i in range(n_samples):
        t = i / (n_samples - 1)        # 0 = top, 1 = bottom
        y = crown_y_top + t * crown_height

        # Phase increases from base to tip so crown tip is the wave origin
        phase = (1.0 - t) * 2.0 * math.pi * n_cycles

        # Harmonic wave (normalized to ~[-1, 1])
        wave = sum(
            weights[n] * math.sin(n * phase + seed_f * n * 2.7)
            for n in range(1, len(weights))
        ) / w_sum

        # Independent Perlin noise per side for organic asymmetry
        noise_l = perlin1d(t * 5.0 + seed_f,        octaves=3, seed=seed)     * 0.10
        noise_r = perlin1d(t * 5.0 + seed_f + 11.3, octaves=3, seed=seed + 1) * 0.10

        base_hw = envelope(t) * max_hw
        hw_l = min(clamp_hw, max(0.0, base_hw * (1.0 + wave * wave_scale + noise_l)))
        hw_r = min(clamp_hw, max(0.0, base_hw * (1.0 + wave * wave_scale + noise_r)))

        left_pts.append((cx - hw_l, y))
        right_pts.append((cx + hw_r, y))

    # --- Build SVG ---
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": f"0 0 {canvas_width} {canvas_height}",
        "width": str(canvas_width),
        "height": str(canvas_height),
    })

    defs = ET.SubElement(svg, "defs")
    ET.SubElement(svg, "rect", {"width": "100%", "height": "100%", "fill": "none"})

    if grad_el is not None:
        defs.append(grad_el)

    # Trunk
    trunk_w_px = min(spec.trunk_width_base * 3.0, canvas_width * 0.05)
    ET.SubElement(svg, "rect", {
        "x":      f"{cx - trunk_w_px / 2:.2f}",
        "y":      f"{crown_y_bottom:.2f}",
        "width":  f"{trunk_w_px:.2f}",
        "height": f"{trunk_px:.2f}",
        "fill":   branch_fill_color,
        "rx":     f"{trunk_w_px * 0.15:.2f}",
    })

    # Waveform polygon: up the left side, down the right side
    all_pts = left_pts + right_pts[::-1]
    poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in all_pts)
    ET.SubElement(svg, "polygon", {
        "points": poly_str,
        "fill":   canopy_fill,
    })

    return svg
