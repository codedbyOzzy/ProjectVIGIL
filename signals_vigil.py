"""Signal sets for VIGIL Stones (TideStone, CompassStone, EmberStone, MirrorStone).

Provides language-specific signal detection for non-English languages.
Based on the same approach used in Intelligence-Stones.

Usage:
    from signals_vigil import VIGILSignals

    # English
    signals = VIGILSignals.EN

    # Turkish
    signals = VIGILSignals.TR

    # Custom
    signals = VIGILSignals(
        frustration_signals=frozenset({"yapamadım", "olmadı"}),
        completion_signals=frozenset({"tamam", "bitirdim"}),
        # ... other signals
    )

    tide = TideStone()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable


@dataclass(frozen=True)
class VIGILSignals:
    """Signal sets for VIGIL Stones.

    Attributes:
        frustration_signals: Words/sentences indicating user frustration
        completion_signals: Words/sentences indicating task completion
        blocked_signals: Words/sentences indicating something is blocked
        goal_patterns: Regex patterns for goal extraction
        decision_signals: Words indicating a decision was made
        revision_signals: Words indicating a decision was changed
    """

    frustration_signals: frozenset[str]
    completion_signals: frozenset[str]
    blocked_signals: frozenset[str]
    goal_patterns: tuple[str, ...]
    decision_signals: frozenset[str]
    revision_signals: frozenset[str]
    normalise_fn: Optional[Callable[[str], str]] = None

    # ── Pre-built configurations ──────────────────────────────────────────

    EN: "VIGILSignals" = None  # defined after class

    TR: "VIGILSignals" = None  # defined after class


VIGILSignals.EN = VIGILSignals(
    frustration_signals=frozenset({
        "frustrated", "annoying", "doesn't work", "failed", "error",
        "stuck", "can't figure out", "impossible", "hate this",
        "yapamadım", "olmadı", "hata", "çözemedim",
    }),
    completion_signals=frozenset({
        "done", "finished", "completed", "solved", "got it working",
        "tamam", "bitirdim", "tamamlandı", "oldu", "halla",
    }),
    blocked_signals=frozenset({
        "blocked", "can't", "impossible", "stuck", "dependency",
        "yapamıyorum", "engeli var", "çalışmıyor",
    }),
    goal_patterns=(
        r"(?:want|will|plan|goal|aim)\s+(.{10,80})",
        r"(?:learn|study|build|create|make)\s+(.{10,80})",
        r"i'm trying to\s+(.{10,80})",
    ),
    decision_signals=frozenset({
        "i'll use", "i decided", "i chose", "going with",
        "i will use", "use ", "seçtim", "kullanacağım",
    }),
    revision_signals=frozenset({
        "actually", "changed my mind", "instead", "revised",
        "fikrimi değiştirdim", "asında değil", "yapmayacağım",
    }),
    normalise_fn=None,
)

VIGILSignals.TR = VIGILSignals(
    frustration_signals=frozenset({
        "yapamadım", "olmadı", "hata aldım", "çalışmıyor",
        "bir türlü", "engeli var", "çözemedim", "üzerinde takılıyorum",
        "frustrated", "annoying", "doesn't work", "failed",
    }),
    completion_signals=frozenset({
        "tamam", "bitirdim", "tamamlandı", "oldu", "halla",
        "done", "finished", "completed", "solved", "got it",
    }),
    blocked_signals=frozenset({
        "yapamıyorum", "engeli var", "çalışmıyor", "mümkün değil",
        "blocked", "can't", "impossible",
    }),
    goal_patterns=(
        r"(?:istem|plan|hedef)\s+(.{10,80})",
        r"(?:öğren|inşa|yarat)\s+(.{10,80})",
        r"(?:want|will|plan|goal|aim)\s+(.{10,80})",
        r"(?:learn|study|build|create|make)\s+(.{10,80})",
    ),
    decision_signals=frozenset({
        "seçtim", "kullanacağım", "karar verdim",
        "i'll use", "i decided", "i chose", "use ",
    }),
    revision_signals=frozenset({
        "fikrimi değiştirdim", "asında değil", "yapmayacağım",
        "actually", "changed my mind", "instead",
    }),
    normalise_fn=None,
)


def _turkish_normalise(text: str) -> str:
    """Normalise Turkish text for comparison (removes diacritics)."""
    replacements = {
        "ç": "c", "ğ": "g", "ı": "i", "ş": "s", "ü": "u",
        "Ç": "c", "Ğ": "g", "İ": "i", "Ş": "s", "Ü": "u",
        "ö": "o",
    }
    for turkish, ascii_replacement in replacements.items():
        text = text.replace(turkish, ascii_replacement)
    return text


# Use Turkish normalise function
VIGILSignals.TR = VIGILSignals(
    frustration_signals=VIGILSignals.TR.frustration_signals,
    completion_signals=VIGILSignals.TR.completion_signals,
    blocked_signals=VIGILSignals.TR.blocked_signals,
    goal_patterns=VIGILSignals.TR.goal_patterns,
    decision_signals=VIGILSignals.TR.decision_signals,
    revision_signals=VIGILSignals.TR.revision_signals,
    normalise_fn=_turkish_normalise,
)