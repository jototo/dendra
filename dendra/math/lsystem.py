"""L-system engine — string rewriting → turtle geometry → DrawCommand lists."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------

@dataclass
class LSystemSpec:
    axiom: str
    rules: dict[str, str]
    angle: float          # base branching angle in degrees
    iterations: int       # default expansion depth
    step_length: float    # base segment length in SVG units
    length_decay: float   # multiplier applied per recursion depth (e.g. 0.7)
    # Optional per-symbol overrides for angle (keyed by symbol)
    angle_overrides: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Draw commands
# ---------------------------------------------------------------------------

@dataclass
class Segment:
    """A line segment from (x0,y0) to (x1,y1) at a given tree depth."""
    x0: float
    y0: float
    x1: float
    y1: float
    depth: int          # recursion depth — used for stroke taper


@dataclass
class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


# ---------------------------------------------------------------------------
# Expansion
# ---------------------------------------------------------------------------

def expand(spec: LSystemSpec, iterations: int | None = None) -> str:
    """Rewrite the axiom for `iterations` generations."""
    n = iterations if iterations is not None else spec.iterations
    result = spec.axiom
    for _ in range(n):
        result = "".join(spec.rules.get(ch, ch) for ch in result)
    return result


# ---------------------------------------------------------------------------
# Turtle interpretation
# ---------------------------------------------------------------------------

AngleModulator = Callable[[float, int, str], float]


def interpret(
    lstring: str,
    spec: LSystemSpec,
    iterations: int | None = None,
    angle_mod: AngleModulator | None = None,
) -> tuple[list[Segment], BoundingBox]:
    """
    Walk the L-system string with a turtle and produce Segment objects.

    angle_mod(base_angle, depth, symbol) → perturbed angle
    """
    n = iterations if iterations is not None else spec.iterations

    # Turtle state: (x, y, heading_degrees, step, depth)
    x, y = 0.0, 0.0
    heading = 90.0          # start pointing up
    step = spec.step_length
    depth = 0

    stack: list[tuple[float, float, float, float, int]] = []
    segments: list[Segment] = []

    all_x = [0.0]
    all_y = [0.0]

    def _angle(symbol: str) -> float:
        base = spec.angle_overrides.get(symbol, spec.angle)
        if angle_mod is not None:
            return angle_mod(base, depth, symbol)
        return base

    for ch in lstring:
        if ch in ("F", "G"):
            # Draw forward
            rad = math.radians(heading)
            nx = x + step * math.cos(rad)
            ny = y - step * math.sin(rad)   # SVG y-axis is inverted
            segments.append(Segment(x, y, nx, ny, depth))
            all_x.extend([x, nx])
            all_y.extend([y, ny])
            x, y = nx, ny

        elif ch == "f":
            # Move forward without drawing
            rad = math.radians(heading)
            x = x + step * math.cos(rad)
            y = y - step * math.sin(rad)

        elif ch == "+":
            heading -= _angle(ch)

        elif ch == "-":
            heading += _angle(ch)

        elif ch == "[":
            stack.append((x, y, heading, step, depth))
            step *= spec.length_decay
            depth += 1

        elif ch == "]":
            x, y, heading, step, depth = stack.pop()

        elif ch == "|":
            heading += 180.0

    bbox = BoundingBox(
        min_x=min(all_x),
        min_y=min(all_y),
        max_x=max(all_x),
        max_y=max(all_y),
    )
    return segments, bbox
