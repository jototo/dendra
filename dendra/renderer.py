"""SVG renderer — assembles DrawCommands + color config into an SVG file.

Design principles:
  - Pure xml.etree, zero external rendering dependencies
  - Stroke width tapers with depth (thick trunk → hairline tips)
  - Fourier crown clipped via SVG clipPath
  - viewBox auto-fits to content with padding
  - Atmospheric: background can be transparent (none) for web overlay use
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from dendra.math.lsystem import LSystemSpec, Segment, BoundingBox, expand, interpret
from dendra.math.wave import note_to_freq, harmonic_weights, modulate_angle
from dendra.math.fractal import drift_point, crown_noise_radii, perlin1d
from dendra.math.fourier import crown_polygon
from dendra.color import ColorConfig, resolve_fill, trunk_fill
from dendra.species.base import TreeSpec


# ---------------------------------------------------------------------------
# Stroke width taper
# ---------------------------------------------------------------------------

def stroke_width(depth: int, max_depth: int, base: float, minimum: float) -> float:
    """Taper stroke linearly from base (depth 0) to minimum (max_depth)."""
    if max_depth == 0:
        return base
    t = depth / max_depth
    return max(minimum, base * (1.0 - t) + minimum * t)


# ---------------------------------------------------------------------------
# Core render function
# ---------------------------------------------------------------------------

def render(
    spec: TreeSpec,
    color: ColorConfig,
    iterations: int | None = None,
    note: str | None = None,
    harmonic_depth: int | None = None,
    seed: int = 0,
    canvas_width: int = 600,
    canvas_height: int = 700,
) -> ET.Element:
    """Generate an SVG Element for the given TreeSpec and parameters.

    Returns the root <svg> Element — call ET.tostring() or write_svg() to export.
    """
    n_iter = iterations if iterations is not None else spec.lsystem.iterations
    note_str = note or spec.default_note
    freq = note_to_freq(note_str)
    n_harm = harmonic_depth if harmonic_depth is not None else spec.wave.n_harmonics
    weights = harmonic_weights(n_harm, spec.wave.harmonic_decay)
    seed_f = float(seed) * 0.137

    # --- Wave modulator ---
    def angle_mod(base_angle: float, depth: int, symbol: str) -> float:
        return modulate_angle(
            base_angle,
            depth,
            freq,
            weights,
            seed_offset=seed_f,
            scale=spec.wave.angle_scale,
        )

    # --- Expand and interpret L-system ---
    lstring = expand(spec.lsystem, n_iter)
    segments, bbox = interpret(lstring, spec.lsystem, n_iter, angle_mod)

    # --- Determine max depth for taper ---
    max_depth = max((s.depth for s in segments), default=1)

    # --- Coordinate transform: fit tree into canvas ---
    tree_w = bbox.width or 1
    tree_h = bbox.height or 1
    trunk_h = canvas_height * spec.crown.trunk_height_ratio

    # Scale to fit, leaving headroom for trunk below
    usable_h = canvas_height - trunk_h - 20
    usable_w = canvas_width - 40
    scale = min(usable_w / tree_w, usable_h / tree_h)

    # Centre horizontally; anchor root (y=0 in turtle space) at bottom of branch area.
    # bbox.min_y is negative (branches grow up = negative SVG y), so we do NOT
    # subtract it here — that was the original bug that pushed everything off-canvas.
    ox = canvas_width / 2 - (bbox.min_x + tree_w / 2) * scale
    oy = canvas_height - trunk_h

    # Crown centre: vertical midpoint of the rendered branch area
    # (bbox.min_y is negative = top of tree, so *0.5 moves halfway up)
    crown_base_y = oy + bbox.min_y * scale * 0.4

    def tx(x: float) -> float:
        return ox + x * scale

    def ty(y: float) -> float:
        return oy + y * scale

    # Apply Perlin drift to segment endpoints (organic wobble).
    # Amplitude is proportional to step_length (turtle units), not SVG scale —
    # so the wobble looks the same regardless of how large the tree is on canvas.
    def drifted(seg: Segment) -> Segment:
        t = seg.depth / (max_depth or 1)
        drift_amp = spec.lsystem.step_length * 0.12 * (1.0 - t)
        x1, y1 = drift_point(seg.x1, seg.y1, t + seed_f, amplitude=drift_amp, seed=seed)
        return Segment(seg.x0, seg.y0, x1, y1, seg.depth)

    segments = [drifted(s) for s in segments]

    # --- Build SVG ---
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": f"0 0 {canvas_width} {canvas_height}",
        "width": str(canvas_width),
        "height": str(canvas_height),
    })

    defs = ET.SubElement(svg, "defs")

    # Background
    bg = ET.SubElement(svg, "rect", {
        "width": "100%",
        "height": "100%",
        "fill": "none",
    })

    # --- Gradient def (if needed) ---
    canopy_fill, grad_el = resolve_fill(color, "dendraGradient")
    if grad_el is not None:
        defs.append(grad_el)

    branch_fill = trunk_fill(color)

    # --- Fourier crown clipPath ---
    clip_id = "crownClip"
    if spec.crown.use_fourier and spec.crown.crown is not None:
        crown_c = spec.crown.crown
        # Cap the polygon scale so large-radius crowns don't spill off canvas.
        crown_poly_scale = min(scale, 2.0)

        # Position crown centre aligned to the actual L-system origin (ox),
        # vertically at the midpoint of the rendered branch area.
        crown_cx = ox + crown_c.cx * scale
        crown_cy = crown_base_y + crown_c.cy * scale

        def noise_fn(t: float, seed: int = 0) -> float:
            return perlin1d(t, octaves=4, seed=seed)

        if spec.crown.clip_branches:
            pts = crown_polygon(
                crown_c,
                n_points=spec.crown.n_points,
                noise_fn=noise_fn if spec.crown.noise_amplitude > 0 else None,
                noise_amplitude=spec.crown.noise_amplitude,
                seed=seed,
            )

            # Scale and translate polygon to canvas
            poly_pts = " ".join(
                f"{crown_cx + x * crown_poly_scale:.2f},{crown_cy + y * crown_poly_scale:.2f}"
                for x, y in pts
            )

            clip_path = ET.SubElement(defs, "clipPath", {"id": clip_id})
            ET.SubElement(clip_path, "polygon", {"points": poly_pts})

    # --- Draw trunk (rect below origin) ---
    # Trunk is anchored at ox (the actual L-system origin x) and capped at 5% canvas width
    # so it never becomes a log even on small/high-scale L-systems.
    trunk_color = branch_fill
    trunk_w_px = min(spec.trunk_width_base * scale * 0.8, canvas_width * 0.05)
    trunk_x = ox - trunk_w_px / 2
    trunk_y = canvas_height - trunk_h
    ET.SubElement(svg, "rect", {
        "x": f"{trunk_x:.2f}",
        "y": f"{trunk_y:.2f}",
        "width": f"{trunk_w_px:.2f}",
        "height": f"{trunk_h:.2f}",
        "fill": trunk_color,
        "rx": f"{trunk_w_px * 0.15:.2f}",
    })

    # --- Draw branches ---
    branch_group = ET.SubElement(svg, "g", {
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
    })
    if spec.crown.use_fourier and spec.crown.clip_branches:
        branch_group.set("clip-path", f"url(#{clip_id})")

    for seg in segments:
        sw = stroke_width(seg.depth, max_depth, spec.trunk_width_base, spec.trunk_width_min)
        # depth 0 (outside all brackets) = trunk spine → branch color
        # depth 1+ (inside any bracket) = foliage → canopy color
        if seg.depth == 0:
            stroke = branch_fill
        else:
            stroke = canopy_fill

        ET.SubElement(branch_group, "line", {
            "x1": f"{tx(seg.x0):.2f}",
            "y1": f"{ty(seg.y0):.2f}",
            "x2": f"{tx(seg.x1):.2f}",
            "y2": f"{ty(seg.y1):.2f}",
            "stroke": stroke,
            "stroke-width": f"{sw * min(scale, 2.5):.2f}",
        })

    # --- Fourier crown fill overlay (semi-transparent canopy mass) ---
    if spec.crown.use_fourier and spec.crown.crown is not None:
        # crown_cx / crown_cy / crown_poly_scale already computed above

        pts = crown_polygon(
            spec.crown.crown,
            n_points=spec.crown.n_points,
            noise_fn=noise_fn if spec.crown.noise_amplitude > 0 else None,
            noise_amplitude=spec.crown.noise_amplitude,
            seed=seed + 1,
        )
        poly_pts = " ".join(
            f"{crown_cx + x * crown_poly_scale:.2f},{crown_cy + y * crown_poly_scale:.2f}"
            for x, y in pts
        )
        ET.SubElement(svg, "polygon", {
            "points": poly_pts,
            "fill": canopy_fill,
            "opacity": "0.18",
        })

    return svg


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------

def write_svg(svg_element: ET.Element, path: Path | str) -> Path:
    """Indent and write the SVG element to a file. Returns the Path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(svg_element, space="  ")
    tree = ET.ElementTree(svg_element)
    tree.write(str(path), encoding="unicode", xml_declaration=False)
    return path


def svg_string(svg_element: ET.Element) -> str:
    """Return the SVG as a string."""
    ET.indent(svg_element, space="  ")
    return ET.tostring(svg_element, encoding="unicode")
