"""Shortleaf Pine (Pinus echinata) — layered conical silhouette.

Uses a two-symbol L-system: A drives the central leader (trunk grows straight up
one step per iteration), B drives lateral whorled branches at 65° from the trunk.
Because lower whorls accumulate more B-iterations than upper ones, the crown
naturally tapers from wide at the base to narrow at the tip — the classic pine cone.
Wave modulation at B5 adds fine rapid texture like needle clusters.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="pine",
    display_name="Shortleaf Pine",
    scientific_name="Pinus echinata",
    silhouette="Tall conical with layered horizontal branch whorls",
    math_engine="L-system (central-leader A/B) + wave modulation",
    lsystem=LSystemSpec(
        axiom="A",
        rules={
            "A": "F[+B][-B]A",   # trunk: one step, add whorl, then continue upward
            "B": "F[+B][-B]",    # lateral branch: one step, then fork
        },
        angle=75.0,
        iterations=6,
        step_length=9.0,
        length_decay=0.62,
    ),
    wave=WaveParams(
        n_harmonics=4,
        harmonic_decay=0.4,
        angle_scale=5.0,    # tight — conifers don't sway much
        length_scale=0.08,
    ),
    crown=CrownParams(
        use_fourier=False,
        noise_amplitude=0.04,
        trunk_height_ratio=0.12,
    ),
    default_palette="winter-silhouette",
    default_note="B5",
    trunk_width_base=8.0,
    trunk_width_min=0.4,
)
