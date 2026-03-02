"""Pawpaw (Asimina triloba) — oval understory clump.

Math: Short-depth L-system (understory tree, not tall) producing a dense
oval clump of branches. Elliptical Fourier envelope (dome compressed
vertically). Wave modulation at a warm mid note.
Default note: A3 — warm mid-range, gentle oscillation.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import dome_crown, FourierCrown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

# Pawpaw crown: oval = dome with vertical compression
_pawpaw_crown = dome_crown(radius=70.0, asymmetry=0.05, flatten=0.4)
_pawpaw_crown.scale = 0.85   # slightly narrower overall

spec = TreeSpec(
    name="pawpaw",
    display_name="Pawpaw",
    scientific_name="Asimina triloba",
    silhouette="Dense oval understory clump with tropical-looking broad leaves",
    math_engine="L-system + Fourier oval crown",
    lsystem=LSystemSpec(
        axiom="X",
        rules={
            "X": "F[+X][-X]FX",
            "F": "FF",
        },
        angle=30.0,
        iterations=4,
        step_length=7.0,
        length_decay=0.70,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.55,
        angle_scale=14.0,
        length_scale=0.12,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=_pawpaw_crown,
        noise_amplitude=0.07,
        trunk_height_ratio=0.15,
    ),
    default_palette="summer-canopy",
    default_note="A3",
    trunk_width_base=6.0,
    trunk_width_min=0.4,
)
