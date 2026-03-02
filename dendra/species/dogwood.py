"""Flowering Dogwood (Cornus florida) — horizontal tiered silhouette.

Uses Plant-2 at a wider angle (30°) than the oak to emphasize flat horizontal
branching tiers. The wider angle makes branches spread more laterally, and
the Fourier tiered crown reinforces the characteristic flat-top outline.
Wave modulation at D4 creates a standing-wave-like rhythm between tiers.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import dome_crown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="dogwood",
    display_name="Flowering Dogwood",
    scientific_name="Cornus florida",
    silhouette="Flat horizontal tiers, understory spreading habit",
    math_engine="L-system (Plant-2, wide angle) + Fourier dome crown",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "F[+F+F]F[-F-F]",
        },
        angle=35.0,
        iterations=4,
        step_length=6.0,
        length_decay=0.70,
    ),
    wave=WaveParams(
        n_harmonics=4,
        harmonic_decay=0.5,
        angle_scale=10.0,
        length_scale=0.12,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=dome_crown(radius=95.0, asymmetry=0.1, flatten=0.35),
        noise_amplitude=0.09,
        trunk_height_ratio=0.15,
        clip_branches=False,
    ),
    default_palette="spring-bloom",
    default_note="D4",
    trunk_width_base=6.0,
    trunk_width_min=0.4,
)
