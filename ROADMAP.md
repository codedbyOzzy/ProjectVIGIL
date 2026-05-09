# VIGIL — Roadmap

> This is an honest roadmap. No hype, no inflated timelines.

---

## Philosophy

VIGIL modules are developed inside [FRIDAY Synapse](https://github.com/codedbyOzzy/ProjectFridaySynapse) first — a production AI assistant running daily. A module ships here only after it's proven in real use.

You get real software. Not prototypes.

---

## Module Status

### 🔥 EMBER — Open Loop Tracker
**Status: Implementation in progress**

- [x] Concept design complete
- [x] Data model defined (Ember object, heat decay function)
- [ ] Core observer loop implementation
- [ ] Heat calculation and decay engine
- [ ] Proactive surfacing logic
- [ ] JSON persistence layer
- [ ] English + Turkish signal configs
- [ ] Test suite (target: 95% coverage)
- [ ] Public release

---

### 🧭 COMPASS — Goal State Engine
**Status: Implementation in progress**

- [x] Concept design complete
- [x] Goal stack model defined
- [ ] Turn-by-turn goal inference
- [ ] Multi-level abstraction (turn → session → project)
- [ ] Directive generation
- [ ] Session persistence
- [ ] Test suite
- [ ] Public release

---

### 🌊 TIDE — Real-Time State Reader
**Status: Implementation in progress**

- [x] Concept design complete
- [x] Signal taxonomy defined (energy, focus, pace)
- [ ] Behavioral signal extraction
- [ ] State profile computation
- [ ] Directive generation
- [ ] Integration with MindStone (long-term + real-time layering)
- [ ] Test suite
- [ ] Public release

---

### 🪞 MIRROR — Self-Uncertainty Tracker
**Status: Design phase**

- [x] Concept design complete
- [ ] Reliability tracking model
- [ ] Domain × tool × question_type taxonomy
- [ ] Confidence score computation
- [ ] Hedge generation
- [ ] Long-term calibration loop
- [ ] Test suite
- [ ] Public release

---

## Release Order

EMBER → COMPASS → TIDE → MIRROR

Rationale: EMBER has the most immediate impact on conversation quality and is furthest along. MIRROR requires the most longitudinal data to be useful, so it ships last.

---

## What Won't Change

- **Zero external dependencies** per module
- **JSON-based persistence** — no database required
- **Language-configurable** signal sets
- **Apache 2.0 license** — free for commercial use

---

## Following Progress

⭐ **Star this repo** — GitHub will notify you on new releases.

No newsletter. No Discord. No waitlist.  
Just commits.

---

*Last updated: May 2026*
