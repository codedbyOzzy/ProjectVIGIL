# Integrating VIGIL Into Your Project

VIGIL is designed to be framework-agnostic. If your project has a conversation loop, VIGIL fits in.

---

## Minimal Integration (Any AI Assistant)

```python
from vigil import Ember, Compass, Tide, Mirror

# Initialize once per user session
ember   = Ember(user_id="user_123")
compass = Compass(user_id="user_123")
tide    = Tide()
mirror  = Mirror(user_id="user_123")

def handle_turn(user_msg: str, system_prompt: str) -> str:
    
    # 1. Observe the turn (updates internal state)
    tide.observe(user_msg)
    compass.observe(user_msg)
    
    # 2. Build awareness context
    awareness = []
    
    active_loops = ember.get_active_context()
    if active_loops:
        awareness.append(active_loops)
    
    goal = compass.get_goal_directive()
    if goal:
        awareness.append(goal)
    
    state = tide.get_state_directive()
    if state:
        awareness.append(state)
    
    confidence = mirror.estimate_confidence(user_msg)
    if confidence.flag:
        awareness.append(confidence.hedge)
    
    # 3. Inject into your system prompt
    if awareness:
        system_prompt += "\n\n[Context]\n" + "\n".join(awareness)
    
    # 4. Call your AI (OpenAI, Gemini, Ollama — anything)
    response = your_llm.complete(system_prompt, user_msg)
    
    # 5. Post-turn observation
    ember.observe(user_msg, response)
    mirror.record(user_msg, response)
    
    return response
```

That's the full integration. No pipeline changes. No framework migration.

---

## Works With

| Platform | Compatible |
|----------|:---------:|
| OpenAI (GPT-4, GPT-4o, o1) | ✅ |
| Google Gemini | ✅ |
| Anthropic Claude | ✅ |
| Groq (Llama, Mixtral, Whisper) | ✅ |
| Ollama (local models) | ✅ |
| Any REST-based LLM API | ✅ |
| LangChain | ✅ |
| LlamaIndex | ✅ |

---

## Using Individual Modules

You don't have to use all four. Each module is independent:

```python
# Just TIDE — real-time state only
from vigil import Tide
tide = Tide()

# Just EMBER — open loop tracking only
from vigil import Ember
ember = Ember(user_id="alice")
```

Pick what you need.

---

## With Intelligence-Stones

VIGIL and [Intelligence-Stones](https://github.com/codedbyOzzy/Intelligence-Stones) are designed to complement each other:

```python
from intelligence_stones import MindStone, BondStone
from vigil import Tide, Ember

# MindStone: who this user is over time
# Tide: who this user is right now
# BondStone: what facts you know about them
# Ember: what's still unresolved for them

# Together: full-spectrum awareness
```

---

## Storage

Each module persists its state to a small JSON file:

```
.ember_state.json     # open loops per user
.compass_state.json   # goal history per user
.tide_state.json      # session state (clears on new session)
.mirror_state.json    # reliability model per user
```

Files are human-readable. Easy to inspect, backup, or wipe.

---

## Performance

All modules are designed for **microsecond-range** overhead on the hot path — signal detection via frozenset lookups and simple arithmetic, not ML inference.

VIGIL never blocks your response pipeline.

---

*Full API documentation will be published alongside each module release.*  
*Follow progress: [ROADMAP.md](ROADMAP.md)*
