# MASTER JSON CONTRACT
# Vedic Astrology Intelligence Framework
**Version:** 2.0 (Staged Pipeline Architecture)

## Purpose
This document defines the absolute, immutable JSON schema that flows through the Unidirectional DAG. Every Engine must conform to this schema. Schema drift is strictly forbidden.

---

## 1. Type A: Static Entity Contract
Used strictly by Phase 3, 4, and 5 (Planets, Houses, Vargas).

```json
{
  "metadata": {
    "entity_id": "string (e.g., 'sun', '1', 'D9')",
    "entity_type": "string (e.g., 'planet', 'house', 'varga')"
  },
  
  // IMMUTABLE D1 PROMISE
  "final_score": 0,       // Integer 0-100 (Clamped)
  "raw_score": 0.0,       // Float (Unclamped, for debugging)
  
  // EXPLAINABILITY 
  // Note: Currently flat for simplicity. Future versions will evolve this into:
  // "breakdown": [{"rule": "exalted", "score": 35, "category": "dignity", "trace": "v1"}]
  "breakdown": {
    "rule_name": 15       // Key-value pairs of exact points added/subtracted
  },
  
  // STRUCTURAL CAPACITY (Math-safe modifiers)
  "modifiers": {
    "varga_bonus": 0.0
  },
  
  // AI CONTEXT & SYNTHESIS TAGS
  "confidence_flags": [
    "string_context_tag",
    "highly_dignified"
  ]
}
```

## Pipeline State Object (The Global Payload)
The `PipelineRunner` manages this global object and passes sections of it to the engines.

```json
{
  "metadata": {},         // Base birth info, ayanamsa, etc.
  "engine_outputs": {
    "planets": {},        // Dictionary of Universal Entity Payloads
    "houses": {},         // Dictionary of Universal Entity Payloads
    "vargas": {},         // Dictionary of Universal Entity Payloads
    "dashas": {},         // Current active periods and multipliers
    "transits": {}        // Snapshot of current/future gochara triggers
  }
}
```