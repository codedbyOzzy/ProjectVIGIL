"""CompassStone — Multi-Turn Goal Tracker for AI Assistants.

> *"Knows where the user is trying to get to — and tracks progress."*

A standalone, zero-dependency Python module that tracks the user's
goals across conversation turns, both session-level and project-level.

Designed to be dropped into any AI assistant project without requiring FRIDAY
or any other system.

Usage:
    from compass_stone import CompassStone

    stone = CompassStone()

    # After each turn:
    stone.observe("I want to learn Python", "Great, let's start with syntax")

    # Before responding:
    directive = stone.get_goal_directive()
    if directive:
        system_prompt += "\n\n" + directive
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_PATH = ".compass_stone.json"
_SAVE_EVERY = 5


# ── Data Structures ────────────────────────────────────────────────────────────

@dataclass
class Goal:
    id: str
    text: str
    created_at: float
    updated_at: float
    status: str  # "active" | "completed" | "blocked" | "abandoned"
    steps: list[str]
    step_statuses: list[str]  # "pending" | "in_progress" | "completed"
    priority: float
    source: str  # "session" | "project"
    mentions: int


# ── Core Class ──────────────────────────────────────────────────────────────

class CompassStone:
    """Tracks user's goals across conversation turns.

    Args:
        path: Persistence file path. Default: ".compass_stone.json"
        save_every: Save to disk every N goal updates. Default: 5
    """

    def __init__(self, path: str | Path = DEFAULT_PATH, save_every: int = _SAVE_EVERY):
        self._path = Path(path)
        self._save_every = save_every
        self._session_goals: list[Goal] = []
        self._project_goals: list[Goal] = []
        self._current_query: str = ""
        self._turn_count: int = 0
        self._save_count: int = 0
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._session_goals = [Goal(**g) for g in data.get("session_goals", [])]
            self._project_goals = [Goal(**g) for g in data.get("project_goals", [])]
        except Exception:
            self._session_goals = []
            self._project_goals = []

    def _save(self) -> None:
        try:
            data = {
                "session_goals": [asdict(g) for g in self._session_goals],
                "project_goals": [asdict(g) for g in self._project_goals],
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

    def _extract_goal_candidates(self, text: str) -> list[str]:
        """Extract potential goal statements from text."""
        candidates = []
        lower = text.lower()

        patterns = [
            r"(?:want|will|plan|hedef|im|trying to|gonna)\s+(.{10,80})",
            r"(?:goal|aim|objective)\s+(?:is\s+)?(.{10,80})",
            r"(?:learn|study|master|build|create|make)\s+(.{10,80})",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, lower, re.IGNORECASE)
            for m in matches:
                cleaned = m.strip().capitalize()
                if len(cleaned) > 10:
                    candidates.append(cleaned)

        return candidates

    def _gen_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]

    # ── Public API ─────────────────────────────────────────────────────────

    def observe(self, user_text: str, ai_text: str = "") -> None:
        """Observe a conversation turn and extract/update goals.

        Args:
            user_text: User's message
            ai_text: Assistant's response (optional)
        """
        text = (user_text or "").strip()
        if not text:
            return

        self._turn_count += 1
        self._current_query = text

        candidates = self._extract_goal_candidates(text)

        for candidate in candidates:
            # Check if goal already exists
            existing = None
            for g in self._session_goals + self._project_goals:
                if candidate.lower() in g.text.lower():
                    existing = g
                    break

            if existing:
                existing.updated_at = time.time()
                existing.mentions += 1
            else:
                new_goal = Goal(
                    id=self._gen_id(),
                    text=candidate,
                    created_at=time.time(),
                    updated_at=time.time(),
                    status="active",
                    steps=[],
                    step_statuses=[],
                    priority=0.5,
                    source="session",
                    mentions=1,
                )
                self._session_goals.append(new_goal)

        # Update existing goals
        for goal in self._session_goals:
            if goal.status == "active":
                # Check for completion signals
                completion_signals = [
                    "tamam", "bitirdim", "yaptım", "oldu", "completed", "finished", "done",
                ]
                if any(signal in text.lower() for signal in completion_signals):
                    goal.status = "completed"

                # Check for blocked signals
                blocked_signals = [
                    "yapamadım", "olmadı", "engel", "blocked", "failed", "can't",
                ]
                if any(signal in text.lower() for signal in blocked_signals):
                    goal.status = "blocked"

        # Save periodically
        self._save_count += 1
        if self._save_count >= self._save_every:
            self._save()
            self._save_count = 0

    def observe_user(self, user_text: str) -> None:
        """Observe only the user message (shorthand).

        Args:
            user_text: User's message
        """
        self.observe(user_text, "")

    def get_goal_directive(self) -> str:
        """Return a directive string describing current goals.

        Returns:
            Directive string for system prompt, or "" if no active goals
        """
        active = [g for g in self._session_goals if g.status == "active"]
        if not active:
            return ""

        lines = ["[COMPASS] User goals:"]
        for g in active[:3]:
            lines.append(f"  - {g.text} ({g.status})")

        return "\n".join(lines)

    def get_active_goals(self) -> list[Goal]:
        """Return list of currently active goals."""
        return [g for g in self._session_goals if g.status == "active"]

    def get_stats(self) -> dict:
        """Get goal statistics."""
        session_active = sum(1 for g in self._session_goals if g.status == "active")
        project_active = sum(1 for g in self._project_goals if g.status == "active")
        completed = sum(1 for g in self._session_goals if g.status == "completed")
        blocked = sum(1 for g in self._session_goals if g.status == "blocked")
        return {
            "active_goals": session_active,
            "project_goals": project_active,
            "completed": completed,
            "blocked": blocked,
        }

    def summary(self) -> dict:
        """Get a human-readable summary."""
        return self.get_stats()

    def reset_session(self) -> None:
        """Clear session goals (keep project goals)."""
        self._session_goals = []
        self._save()

    def reset(self) -> None:
        """Clear all goals."""
        self._session_goals = []
        self._project_goals = []
        self._save()