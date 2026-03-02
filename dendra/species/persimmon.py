"""Persimmon (Diospyros virginiana) — irregular rounded silhouette.

Math: L-system with moderate branching + strong Perlin noise on segment
endpoints to produce the persimmon's rough, slightly chaotic rounded crown.
No strict Fourier envelope — the irregular character is the point.
Wave modulation at a mid-high note gives medium-speed irregular variation.
Default note: C4 (middle C) — balanced, neutral harmonic character.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="persimmon",
    display_name="Persimmon",
    scientific_name="Diospyros virginiana",
    silhouette="Rounded irregular crown, slightly drooping outer branches",
    math_engine="L-system + Perlin noise drift",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "FF-[-F+F+F]+[+F-F-F]",
        },
        angle=28.0,
        iterations=4,
        step_length=6.0,
        length_decay=0.68,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.5,
        angle_scale=10.0,
        length_scale=0.12,
    ),
    crown=CrownParams(
        use_fourier=False,
        noise_amplitude=0.14,
        trunk_height_ratio=0.15,
    ),
    default_palette="ozark-dusk",
    default_note="C4",
    trunk_width_base=8.0,
    trunk_width_min=0.5,
)
