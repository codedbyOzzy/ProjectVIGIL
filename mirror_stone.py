"""MirrorStone — Self-Confidence Tracker for AI Assistants.

> *"Knows when the assistant is confident — and when it's hedging."*

A standalone, zero-dependency Python module that tracks the assistant's
self-confidence per domain by detecting hedging patterns in responses.

Designed to be dropped into any AI assistant project without requiring FRIDAY
or any other system.

Usage:
    from mirror_stone import MirrorStone

    stone = MirrorStone()

    # After each assistant response:
    stone.observe("How does async work?", "It wraps the operation in a coroutine...")

    # Before responding:
    conf = stone.estimate_confidence("python")
    if conf.flag == "low_confidence":
        system_prompt += "\n\n" + stone.get_mirror_directive("python")
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import NamedTuple


# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_PATH = ".mirror_stone.json"
_SAVE_EVERY = 10


# ── Data Structures ────────────────────────────────────────────────────────────

@dataclass
class DomainStats:
    attempts: int = 0
    confident_outcomes: int = 0
    hedging_count: int = 0
    last_seen: float = 0.0


class ConfidenceResult(NamedTuple):
    score: float      # 0.0 - 1.0
    flag: str          # "low_data" | "confident" | "uncertain" | "low_confidence"
    hedge: str         # last hedging phrase detected, or ""


# ── Core Class ──────────────────────────────────────────────────────────────

class MirrorStone:
    """Tracks assistant self-confidence per domain by detecting hedging.

    Args:
        path: Persistence file path. Default: ".mirror_stone.json"
        save_every: Save to disk every N turns. Default: 10
    """

    def __init__(self, path: str | Path = DEFAULT_PATH, save_every: int = _SAVE_EVERY):
        self._path = Path(path)
        self._save_every = save_every
        self._stats: dict[str, DomainStats] = {}
        self._turn_count: int = 0
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            self._stats = {}
            for name, data in raw.get("domains", {}).items():
                self._stats[name] = DomainStats(**data)
        except Exception:
            self._stats = {}

    def _save(self) -> None:
        try:
            data = {
                "domains": {name: asdict(s) for name, s in self._stats.items()},
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

    def _detect_domain(self, text: str) -> str:
        """Detect the domain/topic from text."""
        text_lower = text.lower()

        domains = {
            "python": ["python", "py", "pip", "venv", "asyncio", "django", "flask"],
            "javascript": ["javascript", "js", "node", "npm", "react", "typescript"],
            "web": ["html", "css", "http", "frontend", "backend", "api"],
            "database": ["sql", "postgresql", "mysql", "mongodb", "redis", "query"],
            "docker": ["docker", "container", "kubernetes", "k8s", "dockerfile"],
            "git": ["git", "github", "commit", "branch", "merge", "pull request"],
            "linux": ["linux", "bash", "shell", "terminal", "ubuntu", "unix"],
            "security": ["security", "auth", "encryption", "oauth", "jwt", "ssl"],
            "general": [],
        }

        for domain, keywords in domains.items():
            if domain == "general":
                continue
            if any(kw in text_lower for kw in keywords):
                return domain

        return "general"

    def _has_hedge(self, ai_text: str) -> bool:
        """Detect if AI text contains hedging language."""
        if not ai_text:
            return False

        lower = ai_text.lower()

        hedge_phrases = [
            "i think", "i believe", "i'm not sure", "probably",
            "might be", "could be", "perhaps", "maybe", "it seems",
            "from what i know", "from what i understand", "if i recall",
            "i'm not certain", "i'm not an expert", "you might want to",
            "you could try", "it's possible that", "if that's the case",
            "that would be", "galiba", "sanırım", "olabilir", "belki",
        ]

        return any(phrase in lower for phrase in hedge_phrases)

    def _get_hedge_phrase(self, ai_text: str) -> str:
        """Return the detected hedge phrase, or "". """
        if not ai_text:
            return ""

        lower = ai_text.lower()
        hedge_phrases = [
            "i think", "i believe", "i'm not sure", "probably",
            "might be", "could be", "perhaps", "maybe", "it seems",
            "from what i know", "from what i understand", "if i recall",
            "i'm not certain", "i'm not an expert", "you might want to",
            "you could try", "it's possible that", "if that's the case",
            "that would be", "galiba", "sanırım", "olabilir", "belki",
        ]

        for phrase in hedge_phrases:
            if phrase in lower:
                return phrase

        return ""

    # ── Public API ─────────────────────────────────────────────────────────

    def observe(self, user_text: str, ai_text: str) -> None:
        """Observe a conversation turn and update confidence stats.

        Args:
            user_text: User's message
            ai_text: Assistant's response
        """
        if not user_text or not ai_text:
            return

        self._turn_count += 1
        domain = self._detect_domain(user_text)
        hedged = self._has_hedge(ai_text)

        stats = self._stats.setdefault(domain, DomainStats())
        stats.attempts += 1
        if not hedged:
            stats.confident_outcomes += 1
        stats.last_seen = time.time()

        if self._turn_count % self._save_every == 0:
            self._save()

    def estimate_confidence(self, query: str) -> ConfidenceResult:
        """Estimate confidence for a query/domain.

        Args:
            query: User's message or domain name

        Returns:
            ConfidenceResult with score (0-1), flag, and hedge phrase
        """
        domain = self._detect_domain(query)
        stats = self._stats.get(domain)

        if not stats or stats.attempts < 3:
            return ConfidenceResult(score=0.5, flag="low_data", hedge="")

        conf_ratio = stats.confident_outcomes / stats.attempts

        # Adjust for hedging
        hedge_penalty = min(0.2, stats.hedging_count * 0.02)
        score = max(0.0, conf_ratio - hedge_penalty)

        if score >= 0.7:
            flag = "confident"
        elif score <= 0.3:
            flag = "uncertain"
        else:
            flag = "low_confidence"

        return ConfidenceResult(
            score=round(score, 2),
            flag=flag,
            hedge=self._get_hedge_phrase("") if flag == "low_confidence" else "",
        )

    def get_mirror_directive(self, query: str) -> str:
        """Return a directive based on confidence.

        Args:
            query: User's message or domain name

        Returns:
            Directive string, or "" if confident
        """
        result = self.estimate_confidence(query)

        if result.flag == "low_data":
            return ""
        elif result.flag == "confident":
            return ""
        elif result.flag == "uncertain":
            return "You are uncertain about this topic — be honest and suggest follow-up."
        else:  # low_confidence
            hedge = result.hedge or "hedging"
            return f"You're using hedging language ({hedge}) — be more direct and confident."

    def get_stats(self) -> dict:
        """Get confidence statistics per domain."""
        result = {}
        for domain, stats in self._stats.items():
            conf_ratio = stats.confident_outcomes / stats.attempts if stats.attempts > 0 else 0.0
            result[domain] = {
                "attempts": stats.attempts,
                "confident_ratio": round(conf_ratio, 2),
            }
        return {"total_domains": len(self._stats), "domains": result}

    def summary(self) -> dict:
        """Get a human-readable summary."""
        return self.get_stats()

    def reset(self) -> None:
        """Clear all domain statistics."""
        self._stats = {}
        self._save()