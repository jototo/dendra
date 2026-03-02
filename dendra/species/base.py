"""TreeSpec — the single source of truth for a species' generation parameters."""

from __future__ import annotations

from dataclasses import dataclass, field

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import FourierCrown


@dataclass
class WaveParams:
    n_harmonics: int = 4
    harmonic_decay: float = 0.5     # amplitude falloff per harmonic
    angle_scale: float = 15.0       # max angle perturbation in degrees
    length_scale: float = 0.15      # max length perturbation as fraction


@dataclass
class CrownParams:
    use_fourier: bool = False        # draw Fourier crown envelope
    crown: FourierCrown | None = None
    n_points: int = 128             # crown polygon resolution
    noise_amplitude: float = 0.08   # organic noise applied to crown radii
    trunk_height_ratio: float = 0.3 # trunk as fraction of total SVG height
    clip_branches: bool = True      # apply crown as hard clip-path on branches


@dataclass
class TreeSpec:
    name: str                        # slug (e.g. "white-oak")
    display_name: str                # e.g. "White Oak"
    scientific_name: str             # e.g. "Quercus alba"
    silhouette: str                  # one-line description
    math_engine: str                 # e.g. "L-system + Fourier crown"
    lsystem: LSystemSpec
    wave: WaveParams = field(default_factory=WaveParams)
    crown: CrownParams = field(default_factory=CrownParams)
    default_palette: str = "summer-canopy"
    default_note: str = "A4"
    trunk_width_base: float = 8.0   # SVG stroke-width at depth 0
    trunk_width_min: float = 0.5    # minimum stroke-width at max depth
