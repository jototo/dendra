"""White Oak (Quercus alba) — broad dome silhouette.

Math: L-system with moderate angles and many iterations for dense branching,
clipped by a Fourier dome crown. Wave modulation at a low note produces
slow, wide sweeps that give the oak its characteristic irregular grandeur.
Default note: C2 — deep fundamental, very slow harmonic sweep.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import dome_crown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="white-oak",
    display_name="White Oak",
    scientific_name="Quercus alba",
    silhouette="Massive broad dome with heavy irregular branching",
    math_engine="L-system + Fourier dome crown + wave modulation",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "FF-[-F+F+F]+[+F-F-F]",
        },
        angle=22.5,
        iterations=4,
        step_length=10.0,
        length_decay=0.72,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.6,
        angle_scale=22.0,
        length_scale=0.20,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=dome_crown(radius=140.0, asymmetry=0.15, flatten=0.2),
        noise_amplitude=0.12,
        trunk_height_ratio=0.18,
        clip_branches=False,
    ),
    default_palette="ozark-autumn",
    default_note="C2",
    trunk_width_base=14.0,
    trunk_width_min=0.6,
)
