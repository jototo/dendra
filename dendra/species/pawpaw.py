"""Pawpaw (Asimina triloba) — dense pyramidal understory tree.

Math: Central-leader A/B rule with a double-whorl B
(B → F[+B][-B]F[+B][-B]) produces four lateral sub-branches per tier step
rather than two, creating the dense bushy fullness characteristic of pawpaw.
Angle 58° gives a wide-spreading pyramid clearly distinct from pine (75°)
and cedar (42°). Seven iterations ensures enough top-tier density so the
crown stays full all the way to the tip.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="pawpaw",
    display_name="Pawpaw",
    scientific_name="Asimina triloba",
    silhouette="Dense pyramidal understory crown, four-branch whorls, short trunk",
    math_engine="L-system (central-leader A/B, double-whorl 58°) + wave modulation",
    lsystem=LSystemSpec(
        axiom="A",
        rules={
            "A": "F[+B][-B]A",
            "B": "F[+B][-B]F[+B][-B]",
        },
        angle=58.0,
        iterations=7,
        step_length=6.0,
        length_decay=0.56,
    ),
    wave=WaveParams(
        n_harmonics=3,
        harmonic_decay=0.55,
        angle_scale=8.0,
        length_scale=0.10,
    ),
    crown=CrownParams(
        use_fourier=False,
        noise_amplitude=0.06,
        trunk_height_ratio=0.08,
        clip_branches=False,
    ),
    default_palette="summer-canopy",
    default_note="A3",
    trunk_width_base=7.0,
    trunk_width_min=0.4,
)
