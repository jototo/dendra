"""White Oak (Quercus alba) — massive wide-spreading dome.

Math: Three-way branching rule F[+F][F][-F] — left, center, and right sub-branch
at every node — fills the crown much more densely than a binary split, producing
the solid, rounded canopy mass of a mature white oak. 48° angle gives a wide
horizontal spread without going flat. Wave modulation at C2 (deep low note) adds
slow, heavy sweeps matching the oak's characteristic irregular grandeur.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import dome_crown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="white-oak",
    display_name="White Oak",
    scientific_name="Quercus alba",
    silhouette="Massive wide-spreading dome, dense 3-way branching, short thick trunk",
    math_engine="L-system (3-way F[+F][F][-F], 48°) + Fourier dome + wave modulation",
    lsystem=LSystemSpec(
        axiom="F",
        rules={
            "F": "F[+F][F][-F]",
        },
        angle=48.0,
        iterations=6,
        step_length=8.0,
        length_decay=0.66,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.65,
        angle_scale=28.0,
        length_scale=0.15,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=dome_crown(radius=140.0, asymmetry=0.15, flatten=0.2),
        noise_amplitude=0.14,
        trunk_height_ratio=0.18,
        clip_branches=False,
    ),
    default_palette="ozark-autumn",
    default_note="C2",
    trunk_width_base=14.0,
    trunk_width_min=0.6,
)
