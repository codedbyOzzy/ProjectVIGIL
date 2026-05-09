# VIGIL — Concept Reference

> Deep-dive documentation for each of the four VIGIL modules.

---

## 🔥 EMBER — Open Loop Tracker

### The Problem It Solves

Conversations end. Problems don't always.

A user mentions a deployment issue on Monday. On Wednesday they ask about something unrelated. On Friday they're back — frustrated, circling the same thing. A reactive AI treats each session as independent. EMBER doesn't.

### Core Concept

Every unresolved topic in a conversation creates an **ember** — an internal record of something that started but hasn't finished. Each ember carries a **heat value** (0.0–1.0) that evolves over time:

```
heat increases when:
  - the topic surfaces again in a new conversation
  - the user revisits it with increasing frustration signals
  - time passes without resolution

heat decreases when:
  - explicit resolution is detected ("I fixed it", "never mind", "done")
  - the topic goes silent for an extended period

ember surfaces proactively when:
  - heat exceeds threshold AND session is idle
  - a related topic creates a strong resonance
```

### What It Gives the AI

```python
ember.get_active_context()
# → "You have 2 active open loops:
#    [HIGH] Deployment pipeline issue — 4 days, 3 sessions
#    [MED]  Database migration — 2 days, 1 session"
```

The AI can acknowledge these naturally, connect new questions to ongoing concerns, and surface them when relevant — without being explicitly asked.

### Design Principles

- **No embeddings required** — signal detection via keyword and pattern matching
- **Session-persistent** — survives restarts via JSON storage
- **Graceful decay** — old embers fade naturally, no manual cleanup needed
- **Language-configurable** — resolution signals and topic triggers can be localized

---

## 🧭 COMPASS — Goal State Engine

### The Problem It Solves

Intent parsers categorize *what was said*.  
COMPASS tracks *what is being attempted* — across multiple turns, across sessions.

The same question means different things in different contexts:

```
"What does this error mean?"
  → If COMPASS sees: 2h on the same stack, 6 prior questions
  → Goal state: [active debugging session, high friction]
  → Ideal response: don't explain the error generically — solve it in context

"What does this error mean?"
  → If COMPASS sees: first mention, exploratory tone, new topic
  → Goal state: [learning mode]
  → Ideal response: explain clearly, provide context, invite follow-up
```

Same words. Different responses. That's COMPASS.

### Core Concept

COMPASS maintains a **goal stack** — a running model of what the user is trying to accomplish at multiple levels of abstraction:

```
Level 3 (project):  "Ship this feature by Friday"
Level 2 (session):  "Debug the authentication module"
Level 1 (turn):     "What does KeyError: 'user_id' mean?"
```

Higher levels give lower levels meaning. COMPASS infers levels 2 and 3 from patterns — it doesn't require the user to state them.

### What It Gives the AI

```python
compass.get_goal_directive()
# → "User appears to be in an active debugging session
#    (Level 2 goal inferred). Prioritize direct solutions
#    over explanations. Reference prior context."
```

### Design Principles

- **Multi-turn awareness** — goal state spans the full session, not just the last message
- **Soft inference** — goals are inferred, never demanded from the user
- **Graceful fallback** — when goal is ambiguous, directive is neutral (no false framing)
- **Transparent** — goal state can be logged for debugging

---

## 🌊 TIDE — Real-Time State Reader

### The Problem It Solves

MindStone learns how you communicate over weeks.  
TIDE reads how you're communicating *right now*.

A user who normally prefers detailed explanations might be exhausted at midnight, sending short clipped messages. The long, thorough response they usually want is exactly wrong in that moment.

TIDE is not about who you are. It's about **how you are, right now**.

### Core Concept

TIDE analyzes behavioral signals from the current session and maps them to a **state profile**:

```
Signals observed:
  - Message length trend (getting shorter? longer?)
  - Time between messages (rapid-fire vs. considered)
  - Vocabulary complexity (simple words = cognitive load)
  - Punctuation and capitalization (informal = casual/tired)
  - Time of day × historical pattern for this user
  - Error rate and self-corrections

State profile output:
  - energy:     0.0 (depleted) → 1.0 (high)
  - focus:      0.0 (scattered) → 1.0 (deep focus)
  - pace:       0.0 (slow/exploring) → 1.0 (urgent)
```

### What It Gives the AI

```python
tide.get_state_directive()
# → "User shows low energy signals (short messages, late hour,
#    simplified vocabulary). Recommend: concise responses,
#    lead with the answer, defer detail to follow-up."

# Or:
# → "User in focused flow state (long messages, technical depth,
#    rapid follow-ups). Recommend: match depth, no hand-holding."
```

### Design Principles

- **Session-scoped** — resets each conversation, no cross-session contamination
- **Additive with MindStone** — TIDE for now, MindStone for always
- **No biometric data** — purely text behavioral signals, fully private
- **Conservative by default** — when signals are mixed, directive is neutral

---

## 🪞 MIRROR — Self-Uncertainty Tracker

### The Problem It Solves

AI assistants hallucinate. They hedge inconsistently. They answer a question about chemistry with the same confidence they answer a question about Python — even if one is far outside their reliable range.

The user has no signal for when to trust and when to verify.

MIRROR gives the AI genuine epistemic humility — not as a personality trait, but as a calibrated, empirical model.

### Core Concept

MIRROR tracks the assistant's **reliability by domain and question type**, building a confidence model from observed outcomes:

```
Tracks per [domain × tool × question_type]:
  - correction_rate:    how often was this answer later corrected?
  - consistency_score:  do similar questions get consistent answers?
  - tool_reliability:   how often did this tool return useful output?

Produces:
  - confidence_score:   0.0 (unreliable) → 1.0 (trustworthy)
  - uncertainty_flag:   bool — should the AI signal uncertainty?
  - suggested_hedge:    "You may want to verify this" or None
```

### What It Gives the AI

```python
mirror.estimate_confidence(query="CUDA memory optimization", tool="local_llm")
# → ConfidenceResult(
#     score=0.38,
#     flag=True,
#     hedge="This is outside my reliable range — verify against official docs."
#   )

mirror.estimate_confidence(query="open Chrome browser", tool="desktop_control")
# → ConfidenceResult(
#     score=0.97,
#     flag=False,
#     hedge=None
#   )
```

### Design Principles

- **Empirical, not introspective** — confidence is measured from outcomes, not self-reported
- **Longitudinal** — improves over time as more interactions are observed
- **Non-blocking** — estimates add context, they don't gate responses
- **Transparent to user when relevant** — hedges surface naturally, not anxiously

---

## How the Four Work Together

```
User sends a message
        │
        ├─ TIDE reads the moment
        │    → "Keep it brief, user seems rushed"
        │
        ├─ COMPASS identifies the goal
        │    → "Active debugging session, skip the theory"
        │
        ├─ EMBER checks open loops
        │    → "This might connect to the deployment issue from Tuesday"
        │
        ├─ MIRROR estimates confidence
        │    → "High confidence — no hedge needed"
        │
        └─ Context assembled → AI generates response
             Informed by all four. Invisibly.
```

None of the modules are required. Each adds value independently.  
Together, they give an AI assistant something that's surprisingly rare: **situational awareness**.

---

*All four modules are currently in development as part of [FRIDAY Synapse](https://github.com/codedbyOzzy/ProjectFridaySynapse).*  
*Implementation and release timeline: [ROADMAP.md](ROADMAP.md)*
