"""Usage examples for VIGIL Stones — THE ARC, TideStone, CompassStone, EmberStone, MirrorStone.

These examples show how to integrate each stone into an AI assistant.
All stones are standalone and zero-dependency — use any combination.
"""

from __future__ import annotations

import time

# ── THE ARC ──────────────────────────────────────────────────────────────

print("=" * 60)
print("THE ARC — Long-Term Narrative Tracker")
print("=" * 60)

from the_arc import TheArc, TurnRecord

arc = TheArc(path=".the_arc.json")

# After every conversation turn:
arc.absorb(TurnRecord(
    turn_id=1,
    role="user",
    content="I'll use React Native for the mobile app",
    timestamp=time.time(),
))
arc.absorb(TurnRecord(
    turn_id=2,
    role="assistant",
    content="Great choice! React Native lets you...",
    timestamp=time.time(),
))
arc.absorb(TurnRecord(
    turn_id=3,
    role="user",
    content="Actually, I changed my mind — I'll use Flutter instead",
    timestamp=time.time(),
))

# Before every LLM call:
context = arc.consult("Flutter")
if context:
    print(f"THE ARC context: {context}")

# Get decision context
decisions = arc.get_decision_context("React Native")
print(f"Decisions: {decisions}")

# Statistics
stats = arc.get_stats()
print(f"Stats: {stats}")

# Run decay periodically (e.g., daily)
arc.run_decay()

print()


# ── TideStone ────────────────────────────────────────────────────────────

print("=" * 60)
print("TideStone — Real-Time User State")
print("=" * 60)

from tide_stone import TideStone

tide = TideStone()

# On every user message:
tide.observe_user("I need to learn async Python for my project")
tide.observe_user("Can you explain coroutines?")
tide.observe_user("Thanks")

# Get current state
state = tide.get_state()
if state:
    print(f"Energy: {state.energy}, Pace: {state.pace}, Focus: {state.focus}, Turns: {state.turns}")

# Before responding:
directive = tide.get_state_directive()
if directive:
    print(f"Tide directive: {directive}")

print()


# ── CompassStone ────────────────────────────────────────────────────────

print("=" * 60)
print("CompassStone — Goal Tracker")
print("=" * 60)

from compass_stone import CompassStone

compass = CompassStone(path=".compass_stone.json")

# After each turn:
compass.observe("I want to learn Python this month", "Great goal! Let's start with syntax")
compass.observe("I've been practicing for a week now", "Excellent progress!")
compass.observe("I finished the basics, moving to advanced topics", "")

# Before responding:
goal_directive = compass.get_goal_directive()
if goal_directive:
    print(f"Goal directive: {goal_directive}")

# Active goals
active = compass.get_active_goals()
print(f"Active goals: {len(active)}")

print()


# ── EmberStone ───────────────────────────────────────────────────────────

print("=" * 60)
print("EmberStone — Recurring Topic Heat")
print("=" * 60)

from ember_stone import EmberStone

ember = EmberStone(path=".ember_stone.json")

# After each turn:
ember.observe("I'm working on Python async programming", "Async is powerful...")
ember.observe("Tell me more about async", "Here's how asyncio works...")
ember.observe("What about await?", "await suspends the coroutine...")

# Before responding:
ember_context = ember.get_active_context()
if ember_context:
    print(f"Ember context: {ember_context}")

print()


# ── MirrorStone ─────────────────────────────────────────────────────────

print("=" * 60)
print("MirrorStone — Self-Confidence Tracker")
print("=" * 60)

from mirror_stone import MirrorStone

mirror = MirrorStone(path=".mirror_stone.json")

# After each assistant response:
mirror.observe(
    "How does Python async work?",
    "I think it uses an event loop... it might be based on coroutines... you probably should check the docs"
)

# Before responding:
conf = mirror.estimate_confidence("python async")
print(f"Python confidence: {conf.score} ({conf.flag})")

# Get directive if uncertain
if conf.flag in ("uncertain", "low_confidence"):
    directive = mirror.get_mirror_directive("python async")
    print(f"Mirror directive: {directive}")

print()


# ── Combined Usage ──────────────────────────────────────────────────────

print("=" * 60)
print("Combined — All VIGIL Stones Together")
print("=" * 60)

from the_arc import TheArc, TurnRecord
from tide_stone import TideStone
from compass_stone import CompassStone
from ember_stone import EmberStone
from mirror_stone import MirrorStone

arc = TheArc()
tide = TideStone()
compass = CompassStone()
ember = EmberStone()
mirror = MirrorStone()

def after_each_turn(user_msg: str, assistant_msg: str, turn_id: int):
    """Call after every conversation turn."""
    timestamp = time.time()

    # Track narrative
    arc.absorb(TurnRecord(turn_id=turn_id, role="user", content=user_msg, timestamp=timestamp))
    arc.absorb(TurnRecord(turn_id=turn_id + 1, role="assistant", content=assistant_msg, timestamp=timestamp))

    # Track user state
    tide.observe_user(user_msg)

    # Track goals
    compass.observe(user_msg, assistant_msg)

    # Track hot topics
    ember.observe(user_msg, assistant_msg)

    # Track assistant confidence
    mirror.observe(user_msg, assistant_msg)


def build_system_prompt(base_prompt: str, user_msg: str) -> str:
    """Build enhanced system prompt with all VIGIL context."""
    additions = []

    # THE ARC — narrative context
    arc_ctx = arc.consult(user_msg)
    if arc_ctx:
        additions.append(arc_ctx)

    # TideStone — user state
    tide_directive = tide.get_state_directive()
    if tide_directive:
        additions.append(tide_directive)

    # CompassStone — goals
    goal_directive = compass.get_goal_directive()
    if goal_directive:
        additions.append(goal_directive)

    # EmberStone — hot topics
    ember_ctx = ember.get_active_context()
    if ember_ctx:
        additions.append(ember_ctx)

    # MirrorStone — confidence
    mirror_directive = mirror.get_mirror_directive(user_msg)
    if mirror_directive:
        additions.append(mirror_directive)

    if additions:
        return base_prompt + "\n\n" + "\n\n".join(additions)
    return base_prompt


# Example usage
example_prompt = "You are a helpful AI assistant."
example_user = "I want to build a web app with Python"

enhanced = build_system_prompt(example_prompt, example_user)
print(f"Enhanced prompt:\n{enhanced}")