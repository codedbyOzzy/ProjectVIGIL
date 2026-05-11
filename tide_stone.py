"""TideStone — Real-Time User State Reader for AI Assistants.

> *"Detects energy, focus, and pace from behavioral signals."*

A standalone, zero-dependency Python module that reads the user's current
cognitive/emotional state from message patterns in real-time.

Designed to be dropped into any AI assistant project without requiring FRIDAY
or any other system.

Usage:
    from tide_stone import TideStone

    stone = TideStone()

    # On every user message:
    stone.observe_user("Long detailed message here...")

    # Before responding:
    state = stone.get_state()
    if state:
        directive = stone.get_state_directive()
"""

from __future__ import annotations

import re
import threading
import time
from collections import deque
from typing import NamedTuple


# ── State Result ─────────────────────────────────────────────────────────────

class TideState(NamedTuple):
    energy: str   # "high" | "medium" | "low"
    pace:   str   # "brisk" | "measured" | "relaxed"
    focus:  str   # "sharp" | "normal" | "scattered"
    turns:  int    # how many turns have been observed


# ── Core Class ──────────────────────────────────────────────────────────────

class TideStone:
    """Reads the user's current cognitive/emotional state from message patterns.

    Signals observed per turn:
      - message character length
      - vocabulary complexity (unique ratio x avg word length)
      - inter-message gap (seconds)

    Produces a directive string after MIN_TURNS observations.
    Before that: returns empty string (no data = no noise).

    Args:
        min_turns: Minimum turns before emitting any directive. Default: 3
        max_window: Rolling window size. Default: 12
    """

    MIN_TURNS = 3
    MAX_WINDOW = 12

    def __init__(self, min_turns: int = 3, max_window: int = 12) -> None:
        self.MIN_TURNS = min_turns
        self.MAX_WINDOW = max_window
        self._lengths: deque[int] = deque(maxlen=max_window)
        self._vocab: deque[float] = deque(maxlen=max_window)
        self._timestamps: deque[float] = deque(maxlen=max_window)
        self._lock = threading.Lock()

    # ── Public API ─────────────────────────────────────────────────────────

    def observe_user(self, user_text: str) -> None:
        """Call this on every USER_SPOKE event.

        Args:
            user_text: The user's message text
        """
        text = (user_text or "").strip()
        if not text:
            return
        with self._lock:
            self._lengths.append(len(text))
            self._vocab.append(self._vocab_complexity(text))
            self._timestamps.append(time.time())

    def get_state(self) -> TideState | None:
        """Return current TideState, or None if not enough data.

        Returns:
            TideState with energy/pace/focus/turns, or None if < MIN_TURNS
        """
        with self._lock:
            n = len(self._lengths)
            if n < self.MIN_TURNS:
                return None

            avg_len = sum(self._lengths) / n
            avg_vocab = sum(self._vocab) / n

            # Energy: based on message length and vocabulary complexity
            if avg_len > 150 or avg_vocab > 0.72:
                energy = "high"
            elif avg_len < 40 and avg_vocab < 0.45:
                energy = "low"
            else:
                energy = "medium"

            # Pace: based on inter-message gaps
            gaps = [
                self._timestamps[i] - self._timestamps[i - 1]
                for i in range(1, n)
            ]
            avg_gap = sum(gaps) / len(gaps) if gaps else 30
            if avg_gap < 5:
                pace = "brisk"
            elif avg_gap > 20:
                pace = "relaxed"
            else:
                pace = "measured"

            # Focus: based on vocabulary complexity and message length consistency
            len_variance = self._len_variance()
            if avg_vocab > 0.65 and len_variance < 0.3:
                focus = "sharp"
            elif avg_vocab < 0.40 or len_variance > 0.6:
                focus = "scattered"
            else:
                focus = "normal"

            return TideState(energy=energy, pace=pace, focus=focus, turns=n)

    def get_state_directive(self) -> str:
        """Return a directive string based on current state.

        Returns:
            Directive string for system prompt, or "" if not enough data
        """
        state = self.get_state()
        if state is None:
            return ""

        parts = []

        if state.energy == "low":
            parts.append("User energy appears low — keep responses concise and warm.")
        elif state.energy == "high":
            parts.append("User seems highly engaged — depth is appropriate.")

        if state.pace == "brisk":
            parts.append("User is typing quickly — be direct, avoid long preambles.")
        elif state.pace == "relaxed":
            parts.append("User is taking their time — thorough explanations fit.")

        if state.focus == "sharp":
            parts.append("User focus is sharp — technical depth is welcome.")
        elif state.focus == "scattered":
            parts.append("User focus may be scattered — one clear point at a time.")

        return " ".join(parts) if parts else ""

    def summary(self) -> dict:
        """Get a human-readable summary of current state."""
        state = self.get_state()
        if state is None:
            return {"state": "insufficient_data", "turns": 0}
        return {
            "energy": state.energy,
            "pace": state.pace,
            "focus": state.focus,
            "turns": state.turns,
        }

    def reset(self) -> None:
        """Clear all observed data."""
        with self._lock:
            self._lengths.clear()
            self._vocab.clear()
            self._timestamps.clear()

    # ── Internal Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _vocab_complexity(text: str) -> float:
        """Calculate vocabulary complexity: unique_word_ratio * avg_word_length."""
        words = re.findall(r"\w+", text.lower())
        if not words:
            return 0.0
        unique_ratio = len(set(words)) / len(words)
        avg_len = sum(len(w) for w in words) / len(words)
        return unique_ratio * avg_len / 20.0  # normalized to ~0-1

    def _len_variance(self) -> float:
        """Calculate length variance as coefficient of variation."""
        if not self._lengths:
            return 0.0
        n = len(self._lengths)
        mean = sum(self._lengths) / n
        if mean == 0:
            return 0.0
        variance = sum((x - mean) ** 2 for x in self._lengths) / n
        return (variance ** 0.5) / mean