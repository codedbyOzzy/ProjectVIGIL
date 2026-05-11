"""EmberStone — Recurring Topic Heat Tracker for AI Assistants.

> *"Topics the user keeps returning to — tracked by heat."*

A standalone, zero-dependency Python module that tracks topics the user
keeps returning to, measuring them by "heat" — a value that rises with
attention and decays with silence.

Designed to be dropped into any AI assistant project without requiring FRIDAY
or any other system.

Usage:
    from ember_stone import EmberStone

    stone = EmberStone()

    # After each turn:
    stone.observe("I'm working on the Python project", "Great progress!")

    # Before responding:
    context = stone.get_active_context()
    if context:
        system_prompt += "\n\n" + context
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_PATH = ".ember_stone.json"
ACTIVE_THRESHOLD = 0.25
HEAT_BOOST = 0.15
DECAY_RATE = 0.02
SAVE_EVERY = 5
MAX_EMBERS = 100


# ── Data Structures ────────────────────────────────────────────────────────────

@dataclass
class Ember:
    key: str
    heat: float
    first_seen: float
    last_seen: float
    mentions: int
    resolved: bool
    samples: list[str]


# ── Core Class ──────────────────────────────────────────────────────────────

class EmberStone:
    """Tracks recurring topics as "embers" with heat values.

    Args:
        path: Persistence file path. Default: ".ember_stone.json"
        active_threshold: Minimum heat to be considered active. Default: 0.25
        heat_boost: Heat added each time topic is mentioned. Default: 0.15
        decay_rate: Daily heat decay rate. Default: 0.02
        save_every: Save to disk every N turns. Default: 5
        max_embers: Maximum embers to store. Default: 100
    """

    ACTIVE_THRESHOLD = ACTIVE_THRESHOLD
    HEAT_BOOST = HEAT_BOOST
    DECAY_RATE = DECAY_RATE

    def __init__(
        self,
        path: str | Path = DEFAULT_PATH,
        active_threshold: float = ACTIVE_THRESHOLD,
        heat_boost: float = HEAT_BOOST,
        decay_rate: float = DECAY_RATE,
        save_every: int = SAVE_EVERY,
        max_embers: int = MAX_EMBERS,
    ):
        self._path = Path(path)
        self._active_threshold = active_threshold
        self._heat_boost = heat_boost
        self._decay_rate = decay_rate
        self._save_every = save_every
        self._max_embers = max_embers
        self._embers: dict[str, Ember] = {}
        self._turn_count: int = 0
        self._save_count: int = 0
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._embers = {}
            for item in data.get("embers", []):
                e = Ember(**item)
                self._embers[e.key] = e
        except Exception:
            self._embers = {}

    def _save(self) -> None:
        try:
            data = {
                "embers": [asdict(e) for e in self._embers.values()],
            }
            content = json.dumps(data, ensure_ascii=False, indent=2)

            if self._path.exists() and self._path.stat().st_size > 10:
                import shutil
                backup = self._path.with_suffix(".backup.json")
                shutil.copy2(self._path, backup)

            temp = self._path.with_suffix(".tmp")
            if temp.exists():
                temp.unlink()
            temp.write_text(content, encoding="utf-8")
            import os as _os
            _os.replace(str(temp), str(self._path))
        except Exception:
            pass

    def _normalize_key(self, text: str) -> str:
        """Normalize text into a topic key."""
        text = text.lower().strip()
        stop = {
            "bir", "ve", "ile", "için", "olan", "bu", "ne", "nasıl", "neden",
            "the", "a", "an", "is", "are", "was", "were", "to", "of",
        }
        words = [w for w in re.findall(r"\w+", text) if len(w) > 2 and w not in stop]
        return " ".join(words[:6])

    def _extract_topics(self, text: str) -> list[str]:
        """Extract candidate topic phrases from text."""
        text_lower = text.lower()

        # Look for noun-like clusters
        patterns = [
            r"\b([a-z]{4,}(?:\s+[a-z]{4,}){0,2})\b",
        ]

        topics = []
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            topics.extend(matches)

        # Filter out very short or generic
        topics = [t.strip() for t in topics if len(t) > 4]

        return topics[:3]  # max 3 topics per turn

    def _find_similar(self, key: str) -> Optional[Ember]:
        """Find an existing ember similar to the key (Jaccard)."""
        key_words = set(key.split())
        for ember in self._embers.values():
            ember_words = set(ember.key.split())
            if not key_words or not ember_words:
                continue
            jaccard = len(key_words & ember_words) / len(key_words | ember_words)
            if jaccard > 0.4:
                return ember
        return None

    def _apply_time_decay(self) -> None:
        """Apply time-based decay to all embers."""
        now = time.time()
        for ember in self._embers.values():
            days_idle = (now - ember.last_seen) / 86400
            if days_idle > 0:
                ember.heat = max(0.0, ember.heat - self._decay_rate * days_idle)

    def _prune(self) -> None:
        """Remove cold embers if over max."""
        if len(self._embers) <= self._max_embers:
            return
        sorted_embers = sorted(self._embers.values(), key=lambda e: e.heat)
        to_remove = len(self._embers) - self._max_embers
        for _ in range(to_remove):
            if sorted_embers:
                ember = sorted_embers.pop(0)
                del self._embers[ember.key]

    def _check_resolution(self, text: str) -> None:
        """Check if any ember was resolved."""
        resolve_signals = [
            "tamam", "bitirdim", "çözdüm", "oldu", "halla",
            "done", "finished", "solved", "completed", "resolved",
        ]
        text_lower = text.lower()
        for ember in self._embers.values():
            if ember.resolved:
                continue
            if any(signal in text_lower for signal in resolve_signals):
                if ember.key in text_lower:
                    ember.resolved = True
                    ember.heat = max(0.0, ember.heat - 0.3)

    # ── Public API ─────────────────────────────────────────────────────────

    def observe(self, user_text: str, ai_text: str = "") -> None:
        """Observe a conversation turn and update ember heat.

        Args:
            user_text: User's message
            ai_text: Assistant's response (optional)
        """
        text = (user_text or "").strip()
        if not text:
            return

        self._turn_count += 1
        self._apply_time_decay()

        topics = self._extract_topics(text)

        for topic in topics:
            key = self._normalize_key(topic)
            if not key:
                continue

            existing = self._find_similar(key)
            if existing:
                existing.heat = min(1.0, existing.heat + self._heat_boost)
                existing.last_seen = time.time()
                existing.mentions += 1
                if len(existing.samples) < 5:
                    existing.samples.append(text[:80])
            else:
                new_ember = Ember(
                    key=key,
                    heat=0.3,
                    first_seen=time.time(),
                    last_seen=time.time(),
                    mentions=1,
                    resolved=False,
                    samples=[text[:80]],
                )
                self._embers[key] = new_ember
                self._prune()

        self._check_resolution(text)

        if self._turn_count % self._save_every == 0:
            self._save()

    def observe_user(self, user_text: str) -> None:
        """Observe only the user message (shorthand)."""
        self.observe(user_text, "")

    def get_active_context(self) -> str:
        """Return directive string with active (hot) embers.

        Returns:
            Directive string listing unresolved hot topics, or "" if none
        """
        self._apply_time_decay()

        active = [
            e for e in self._embers.values()
            if not e.resolved and e.heat >= self._active_threshold
        ]
        active.sort(key=lambda e: e.heat, reverse=True)

        if not active:
            return ""

        lines = ["[EMBER] Recurring topics:"]
        for e in active[:3]:
            age_days = (time.time() - e.first_seen) / 86400
            age_str = f"{int(age_days)}d" if age_days >= 1 else "today"
            heat_label = "HOT" if e.heat > 0.65 else "WARM"
            lines.append(f"  - {e.key} [{heat_label}, {e.mentions} mentions, {age_str}]")

        return "\n".join(lines)

    def get_embers(self) -> list[Ember]:
        """Return all embers (for inspection)."""
        return list(self._embers.values())

    def get_stats(self) -> dict:
        """Get ember statistics."""
        active = sum(1 for e in self._embers.values() if not e.resolved and e.heat >= self._active_threshold)
        return {
            "total_topics": len(self._embers),
            "active_topics": active,
            "resolved": sum(1 for e in self._embers.values() if e.resolved),
        }

    def summary(self) -> dict:
        """Get a human-readable summary."""
        return self.get_stats()

    def reset(self) -> None:
        """Clear all embers."""
        self._embers = {}
        self._save()