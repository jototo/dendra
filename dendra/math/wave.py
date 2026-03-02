"""Wave modulation — apply musical harmonics to L-system branch angles and lengths.

A musical note defines a fundamental frequency. The harmonic series built from
that frequency modulates branch angles at each recursion depth, so the tree is
literally "tuned" to a pitch. Higher notes → tighter, faster oscillations.
Lower notes → slow, wide sweeps.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Note → frequency
# ---------------------------------------------------------------------------

# MIDI note 69 = A4 = 440 Hz
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_freq(note: str) -> float:
    """Convert a note name like 'A4', 'C#3', 'Bb2' to Hz.

    Supports sharps (#) and flats (b).
    """
    note = note.strip()

    # Separate pitch class from octave
    if len(note) >= 2 and note[1] in ("#", "b"):
        pitch, octave_str = note[:2], note[2:]
    else:
        pitch, octave_str = note[0], note[1:]

    pitch = pitch.upper()

    # Normalise flats to sharps
    flat_map = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B"}
    pitch = flat_map.get(pitch, pitch)

    if pitch not in _NOTE_NAMES:
        raise ValueError(f"Unrecognised pitch class: {pitch!r}")

    try:
        octave = int(octave_str)
    except ValueError:
        raise ValueError(f"Unrecognised octave in note: {note!r}")

    semitones_from_a4 = (_NOTE_NAMES.index(pitch) - _NOTE_NAMES.index("A")) + (octave - 4) * 12
    return 440.0 * (2 ** (semitones_from_a4 / 12))


# ---------------------------------------------------------------------------
# Harmonic modulation
# ---------------------------------------------------------------------------

def harmonic_weights(n_harmonics: int, decay: float = 0.5) -> list[float]:
    """Generate a harmonic weight vector with amplitude decay.

    harmonic k has weight decay^(k-1), mimicking the natural overtone series.
    """
    return [decay ** (k - 1) for k in range(1, n_harmonics + 1)]


def modulate_angle(
    base_angle: float,
    depth: int,
    frequency: float,
    weights: list[float],
    seed_offset: float = 0.0,
    scale: float = 15.0,
) -> float:
    """Perturb base_angle using a Fourier-style harmonic series.

    Args:
        base_angle:   The species' default branch angle in degrees.
        depth:        Current recursion depth in the L-system stack.
        frequency:    Fundamental frequency in Hz (from note_to_freq).
        weights:      Harmonic amplitude weights (see harmonic_weights).
        seed_offset:  Phase offset per-tree seed for variation.
        scale:        Max perturbation in degrees across all harmonics.

    Returns:
        Perturbed angle in degrees.
    """
    # Normalise frequency to [0,1] range so perturbation is independent of
    # absolute pitch. We map across a useful musical range (20–2000 Hz).
    t = (depth + seed_offset) * (frequency / 440.0)

    perturbation = sum(
        w * math.sin(2 * math.pi * k * t)
        for k, w in enumerate(weights, start=1)
    )

    # Normalise by sum of weights so total amplitude stays in [-scale, +scale]
    weight_sum = sum(abs(w) for w in weights) or 1.0
    return base_angle + scale * (perturbation / weight_sum)


def modulate_length(
    base_length: float,
    depth: int,
    frequency: float,
    weights: list[float],
    seed_offset: float = 0.0,
    scale: float = 0.2,
) -> float:
    """Perturb branch step length using the harmonic series.

    Returns a multiplier in roughly [1-scale, 1+scale].
    """
    t = (depth + seed_offset + 0.5) * (frequency / 440.0)

    perturbation = sum(
        w * math.cos(2 * math.pi * k * t)
        for k, w in enumerate(weights, start=1)
    )

    weight_sum = sum(abs(w) for w in weights) or 1.0
    multiplier = 1.0 + scale * (perturbation / weight_sum)
    return base_length * max(0.1, multiplier)
