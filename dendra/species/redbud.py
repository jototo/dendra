"""Eastern Redbud (Cercis canadensis) — spreading vase silhouette.

Uses Plant-2 at 25° with 5 iterations for a denser, more spreading crown than
the oak. The vase Fourier envelope shapes the wide low canopy characteristic of
redbud. Wave modulation at E3 (warm low harmonic) produces gentle lateral sway.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.math.fourier import vase_crown
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="redbud",
    display_name="Eastern Redbud",
    scientific_name="Cercis canadensis",
    silhouette="Spreading vase with dense horizontal branches",
    math_engine="L-system (Plant-2) + wave modulation + Fourier vase crown",
    lsystem=LSystemSpec(
        axiom="[+F][-F]",
        rules={
            "F": "FF-[-F+F+F]+[+F-F-F]",
        },
        angle=36.0,
        iterations=4,
        step_length=5.5,
        length_decay=0.65,
    ),
    wave=WaveParams(
        n_harmonics=4,
        harmonic_decay=0.55,
        angle_scale=15.0,
        length_scale=0.12,
    ),
    crown=CrownParams(
        use_fourier=True,
        crown=vase_crown(radius=65.0, spread=1.3),
        noise_amplitude=0.10,
        trunk_height_ratio=0.15,
        clip_branches=False,
    ),
    default_palette="spring-bloom",
    default_note="E3",
    trunk_width_base=7.0,
    trunk_width_min=0.5,
)
