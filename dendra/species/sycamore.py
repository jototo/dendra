"""Sycamore (Platanus occidentalis) — tall, asymmetric spread.

Math: L-system with large irregular angles and Perlin-drifted endpoints
producing the sycamore's characteristic wild, asymmetric crown. Fourier
dome with strong asymmetry term. Wave modulation at a low-mid note gives
slow irregular sway to the heavy limbs.
Default note: F2 — low-mid, slow sweep with noticeable 2nd harmonic character.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import dome_crown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="sycamore",
    display_name="Sycamore",
    scientific_name="Platanus occidentalis",
    silhouette="Tall with massive irregular asymmetric spreading crown",
    math_engine="L-system + Perlin drift + Fourier asymmetric dome",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "FF-[-F+F+F]+[+F-F-F]",
        },
        angle=25.7,
        iterations=4,
        step_length=11.0,
        length_decay=0.75,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.65,
        angle_scale=28.0,
        length_scale=0.22,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=dome_crown(radius=155.0, asymmetry=0.35, flatten=0.05),
        noise_amplitude=0.16,
        trunk_height_ratio=0.20,
        clip_branches=False,
    ),
    default_palette="ozark-autumn",
    default_note="F2",
    trunk_width_base=16.0,
    trunk_width_min=0.7,
)
