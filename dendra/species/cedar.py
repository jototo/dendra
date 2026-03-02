"""Eastern Red Cedar (Juniperus virginiana) — dense narrow pyramidal silhouette.

Uses the same central-leader A/B rule as pine but with a tighter branch angle (42°)
and more iterations (7), making the tiers shorter, denser, and more compressed
vertically. The narrower angle produces the compact pyramidal cone characteristic
of eastern red cedar — clearly different from the open horizontal whorls of pine.
High-frequency wave modulation (G5) adds fine-grained texture like scale foliage.
"""

from dendra.math.lsystem import LSystemSpec
from dendra.species.base import TreeSpec, WaveParams, CrownParams

spec = TreeSpec(
    name="cedar",
    display_name="Eastern Red Cedar",
    scientific_name="Juniperus virginiana",
    silhouette="Dense narrow pyramid, tiered evergreen",
    math_engine="L-system (central-leader A/B, tight 42°) + wave modulation",
    lsystem=LSystemSpec(
        axiom="A",
        rules={
            "A": "F[+B][-B]A",   # trunk: one step, add whorl, then continue upward
            "B": "F[+B][-B]",    # dense sub-branching
        },
        angle=42.0,
        iterations=7,
        step_length=6.0,
        length_decay=0.55,
    ),
    wave=WaveParams(
        n_harmonics=6,
        harmonic_decay=0.4,
        angle_scale=4.0,
        length_scale=0.08,
    ),
    crown=CrownParams(
        use_fourier=False,
        noise_amplitude=0.05,
        trunk_height_ratio=0.10,
    ),
    default_palette="ink-wash",
    default_note="G5",
    trunk_width_base=7.0,
    trunk_width_min=0.3,
)
