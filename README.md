<div align="center">

# ◈ VIGIL

### *The Awareness Layer for AI Assistants*

**What if your AI assistant could notice things — without being asked?**

[![Status](https://img.shields.io/badge/status-v1.0--released-green?style=flat-square)](https://github.com/codedbyOzzy/ProjectVIGIL)
[![Built on](https://img.shields.io/badge/built%20on-Intelligence--Stones-blue?style=flat-square)](https://github.com/codedbyOzzy/Intelligence-Stones)
[![License](https://img.shields.io/badge/license-Apache%202.0-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/codedbyOzzy/ProjectVIGIL?style=flat-square)](https://github.com/codedbyOzzy/ProjectVIGIL/stargazers)

</div>

---

## The Problem

Most AI assistants are reactive. They wait for you to speak, respond to what you said, and move on.

They don't notice that you've been struggling with the same problem for three days.  
They don't adjust when you're exhausted at 1am versus focused at 10am.  
They answer with equal confidence whether they're certain or guessing.  
They respond to your *words* — not to what you're actually trying to accomplish.

**VIGIL is built to close that gap.**

---

## What Is VIGIL?

VIGIL is an **open-source awareness layer** — a system of four independent modules that run silently alongside any AI assistant, giving it genuine depth of understanding.

Not memory. Not personality. Not another chatbot wrapper.

Something that lives *between* conversations. *Beneath* the words. Always watching. Always learning.

```
┌─────────────────────────────────────────────────────────────┐
│                          VIGIL                              │
│                                                             │
│   🔥 EMBER      What remains unresolved                    │
│   🧭 COMPASS    Where you're actually headed                │
│   🌊 TIDE       How the user is — right now                 │
│   🪞 MIRROR     What the AI doesn't know about itself       │
│                                                             │
│              [ Your AI Assistant ]                          │
│         ↑ colored by everything above ↑                     │
└─────────────────────────────────────────────────────────────┘
```

Each module is **standalone**, **zero-dependency**, and can be integrated into **any AI assistant project** — not just FRIDAY.

---

## The Four Modules

### 🔥 EMBER — Open Loop Tracker
> *"Some things don't close. EMBER keeps watching them."*

Detects unresolved topics, unfinished tasks, and recurring concerns across conversations. Each *ember* has a heat level — it glows brighter when related topics surface, fades when resolved, and surfaces proactively when it's been burning too long.

→ [Read full concept](CONCEPTS.md#-ember--open-loop-tracker)

---

### 🧭 COMPASS — Goal State Engine
> *"You asked what. COMPASS knows why."*

Tracks the user's actual goal across multiple conversation turns — not the command they issued, but what they're genuinely trying to accomplish. A debugging session is different from a learning session, even when the words look the same.

→ [Read full concept](CONCEPTS.md#-compass--goal-state-engine)

---

### 🌊 TIDE — Real-Time State Reader
> *"It's 1am and you've sent 4 short messages in a row. TIDE knows."*

Reads the user's current cognitive and emotional state from behavioral signals — message length, response cadence, vocabulary complexity, time of day — and adjusts the assistant's output depth accordingly. Not long-term style learning. The *current moment*, right now.

→ [Read full concept](CONCEPTS.md#-tide--real-time-state-reader)

---

### 🪞 MIRROR — Self-Uncertainty Tracker
> *"Knowing what you don't know is the beginning of real intelligence."*

Tracks where the AI assistant produces unreliable, inconsistent, or later-corrected answers. Builds a confidence model: which domains, tools, and question types are trustworthy — and which warrant explicit uncertainty signals to the user.

→ [Read full concept](CONCEPTS.md#-mirror--self-uncertainty-tracker)

---

## How It Fits Into Your Project

VIGIL is designed to be **dropped into any AI assistant pipeline**:

```python
# Anywhere in your AI assistant loop:

from vigil import Ember, Compass, Tide, Mirror

ember   = Ember()
compass = Compass()
tide    = Tide()
mirror  = Mirror()

# After each conversation turn:
ember.observe(user_msg, assistant_msg)
compass.observe(user_msg, assistant_msg)
tide.observe(user_msg)

# Before generating a response:
context = ""
context += ember.get_active_context()    # "User has 2 unresolved topics"
context += compass.get_goal_directive()  # "User is in debugging mode"
context += tide.get_state_directive()    # "Keep it short — user seems tired"

confidence = mirror.estimate(query, tool)
if confidence < 0.4:
    context += "Acknowledge uncertainty in your response."

# Inject context into your system prompt — done.
```

No framework lock-in. No cloud dependency. No ML training required.  
Works with OpenAI, Gemini, Ollama, Groq — or anything else.

---

## Relationship to Intelligence-Stones

VIGIL builds on top of [Intelligence-Stones](https://github.com/codedbyOzzy/Intelligence-Stones) — the cognitive adaptation layer (MindStone, EchoStone, BondStone, IntuitionStone).

```
Intelligence-Stones  →  WHO the user is (long-term style, preferences, world model)
VIGIL                →  WHAT IS HAPPENING right now, beneath the surface
```

Both systems together: an assistant that knows you *and* understands the moment.

---

## Powered by FRIDAY Synapse

VIGIL is being actively developed as part of [FRIDAY Synapse](https://github.com/codedbyOzzy/ProjectFridaySynapse) — a Windows-native AI desktop assistant. Every VIGIL module is validated in production before release.

You get battle-tested code, not theoretical design.

---

## Status

| Module | Design | Implementation | Testing | Release |
|--------|:------:|:--------------:|:-------:|:-------:|
| 🔥 EMBER | ✅ | ✅ | ✅ | ✅ |
| 🧭 COMPASS | ✅ | ✅ | ✅ | ✅ |
| 🌊 TIDE | ✅ | ✅ | ✅ | ✅ |
| 🪞 MIRROR | ✅ | ✅ | ✅ | ✅ |

`✅ Done` · `🔄 In Progress` · `⏳ Planned`

---

## Who Is This For?

- Developers building AI assistants or chatbot products
- Anyone integrating LLMs into long-running, multi-session applications
- Researchers exploring persistent context and user-aware AI
- Anyone who's thought *"why doesn't my AI just notice that?"*

---

## Stay Updated

**⭐ Star this repository** to get notified when modules ship.

Code will be released here — no newsletter, no waitlist, no gatekeeping.  
Just good software, when it's ready.

---

## License

Apache 2.0 — free to use in personal and commercial projects.

---

<div align="center">

*"A good assistant doesn't wait to be told everything.*  
*It pays attention."*

**— VIGIL**

</div>
