"""Sycamore (Platanus occidentalis) — tall dense rounded crown.

Math: Four-way branching rule F[+F][-F][++F][--F] fires two pairs of branches
at every node — narrow (30°) and wide (60°). The two angle levels break up
geometric regularity, producing the irregular lumpy masses characteristic of
a mature sycamore's crown. Five iterations gives a solid, filled oval without
large internal voids. Wave modulation at F2 adds slow heavy sway.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="sycamore",
    display_name="Sycamore",
    scientific_name="Platanus occidentalis",
    silhouette="Tall dense rounded crown with irregular lumpy masses",
    math_engine="L-system (4-way F[+F][-F][++F][--F], 30°) + wave modulation",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "F[+F][-F][++F][--F][++++++F]",
        },
        angle=30.0,
        iterations=4,
        step_length=8.0,
        length_decay=0.66,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.65,
        angle_scale=28.0,
        length_scale=0.22,
    ),
    crown=CrownParams(
        use_fourier=False,
        noise_amplitude=0.16,
        trunk_height_ratio=0.22,
        clip_branches=False,
    ),
    default_palette="ozark-autumn",
    default_note="F2",
    trunk_width_base=16.0,
    trunk_width_min=0.7,
)
