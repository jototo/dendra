"""Color system — named palettes, single hex fills, and SVG gradient builders.

Design principle (from agents.md): commit to bold, cohesive palettes.
Dominant colors with sharp accents. No timid, evenly-distributed schemes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Palette definitions
# ---------------------------------------------------------------------------

@dataclass
class Palette:
    name: str
    display: str                # human-readable name
    trunk: str                  # hex — trunk/branch fill
    canopy: str                 # hex — primary canopy/leaf fill
    canopy_accent: str          # hex — secondary canopy accent
    background: str             # hex — SVG background (can be "none")
    border_accent: str          # hex — used for Rich CLI panel borders


PALETTES: dict[str, Palette] = {
    "ozark-autumn": Palette(
        name="ozark-autumn",
        display="Ozark Autumn",
        trunk="#3d2314",
        canopy="#b5451b",
        canopy_accent="#e8922a",
        background="none",
        border_accent="#e8922a",
    ),
    "winter-silhouette": Palette(
        name="winter-silhouette",
        display="Winter Silhouette",
        trunk="#1a1a1a",
        canopy="#2c2c2c",
        canopy_accent="#4a4a4a",
        background="none",
        border_accent="#8a8a8a",
    ),
    "spring-bloom": Palette(
        name="spring-bloom",
        display="Spring Bloom",
        trunk="#4a2c1a",
        canopy="#c4587a",
        canopy_accent="#f2a7bf",
        background="none",
        border_accent="#f2a7bf",
    ),
    "summer-canopy": Palette(
        name="summer-canopy",
        display="Summer Canopy",
        trunk="#2d1a0e",
        canopy="#2d5a1b",
        canopy_accent="#5a8c3c",
        background="none",
        border_accent="#5a8c3c",
    ),
    "bare-bones": Palette(
        name="bare-bones",
        display="Bare Bones",
        trunk="#f5f0e8",
        canopy="#ddd5c0",
        canopy_accent="#b8a990",
        background="none",
        border_accent="#b8a990",
    ),
    "ink-wash": Palette(
        name="ink-wash",
        display="Ink Wash",
        trunk="#0d0d0d",
        canopy="#1f2d1f",
        canopy_accent="#2e4a2e",
        background="none",
        border_accent="#3d6b3d",
    ),
    "ozark-dusk": Palette(
        name="ozark-dusk",
        display="Ozark Dusk",
        trunk="#1c1226",
        canopy="#3d2459",
        canopy_accent="#7a4fa0",
        background="none",
        border_accent="#a87fd4",
    ),
}

DEFAULT_PALETTE = "summer-canopy"


def get_palette(name: str) -> Palette:
    if name not in PALETTES:
        names = ", ".join(PALETTES.keys())
        raise ValueError(f"Unknown palette {name!r}. Available: {names}")
    return PALETTES[name]


# ---------------------------------------------------------------------------
# Color mode resolution
# ---------------------------------------------------------------------------

@dataclass
class ColorConfig:
    mode: Literal["palette", "flat", "gradient"]
    palette: Palette | None = None
    flat_color: str | None = None          # hex
    gradient_start: str | None = None      # hex
    gradient_end: str | None = None        # hex
    gradient_direction: Literal["vertical", "horizontal", "diagonal"] = "vertical"


def parse_color_config(
    palette: str | None = None,
    color: str | None = None,
    gradient: str | None = None,
) -> ColorConfig:
    """Resolve CLI color flags into a ColorConfig.

    Precedence: gradient > flat color > palette.
    gradient format: "#rrggbb:#rrggbb:vertical|horizontal|diagonal"
    """
    if gradient:
        parts = gradient.split(":")
        if len(parts) < 2:
            raise ValueError("gradient must be 'start:end' or 'start:end:direction'")
        start = parts[0].strip()
        end = parts[1].strip()
        direction = parts[2].strip() if len(parts) > 2 else "vertical"
        if direction not in ("vertical", "horizontal", "diagonal"):
            direction = "vertical"
        _validate_hex(start)
        _validate_hex(end)
        return ColorConfig(
            mode="gradient",
            gradient_start=start,
            gradient_end=end,
            gradient_direction=direction,
        )

    if color:
        _validate_hex(color)
        return ColorConfig(mode="flat", flat_color=color)

    pal_name = palette or DEFAULT_PALETTE
    return ColorConfig(mode="palette", palette=get_palette(pal_name))


def _validate_hex(h: str) -> None:
    if not re.match(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$", h):
        raise ValueError(f"Invalid hex color: {h!r}. Expected #rgb or #rrggbb.")


# ---------------------------------------------------------------------------
# SVG gradient builder
# ---------------------------------------------------------------------------

def build_gradient_def(
    gradient_id: str,
    start: str,
    end: str,
    direction: Literal["vertical", "horizontal", "diagonal"] = "vertical",
) -> ET.Element:
    """Return a <linearGradient> Element for insertion into SVG <defs>."""
    coords = {
        "vertical":   dict(x1="0", y1="0", x2="0", y2="1"),
        "horizontal": dict(x1="0", y1="0", x2="1", y2="0"),
        "diagonal":   dict(x1="0", y1="0", x2="1", y2="1"),
    }[direction]

    grad = ET.Element("linearGradient", {
        "id": gradient_id,
        "gradientUnits": "objectBoundingBox",
        **coords,
    })
    stop1 = ET.SubElement(grad, "stop", {"offset": "0%", "stop-color": start})
    stop2 = ET.SubElement(grad, "stop", {"offset": "100%", "stop-color": end})
    return grad


def resolve_fill(config: ColorConfig, gradient_id: str = "treeGradient") -> tuple[str, ET.Element | None]:
    """Return (fill_value, optional_gradient_element).

    fill_value is either a hex string or "url(#gradient_id)".
    """
    if config.mode == "flat":
        return config.flat_color, None

    if config.mode == "gradient":
        grad = build_gradient_def(
            gradient_id,
            config.gradient_start,
            config.gradient_end,
            config.gradient_direction,
        )
        return f"url(#{gradient_id})", grad

    # palette mode — use canopy color for fill, trunk for stroke
    return config.palette.canopy, None


def trunk_fill(config: ColorConfig) -> str:
    """Return trunk/branch fill color."""
    if config.mode == "palette":
        return config.palette.trunk
    if config.mode == "flat":
        return config.flat_color
    # gradient: darker stop for trunk
    return config.gradient_start


def accent_color(config: ColorConfig) -> str:
    """Return accent color for Rich CLI panel borders."""
    if config.mode == "palette":
        return config.palette.border_accent
    if config.mode == "flat":
        return config.flat_color
    return config.gradient_end
