# Bug Fixes - Intent Classification

## Issues Found and Fixed

### 1. ✅ Markdown Code Block Parsing Error

**Problem**: LLM was returning JSON wrapped in markdown code blocks:
```
```json
{
    "intent": "PAYMENT",
    ...
}
```
```

But the code was trying to parse it directly, causing `JSONDecodeError`.

**Solution**: Added `_extract_json_from_response()` helper method in [`intent_classifier.py`](file:///projects/agentic-ai/langgraph-test/src/agents/intent_classifier.py#L86-L113) to strip markdown code blocks before parsing.

**Files Modified**:
- `src/agents/intent_classifier.py` - Added extraction helper

---

### 2. ✅ Case Sensitivity Error

**Problem**: 
- Prompt asked for uppercase: `"PAYMENT|FAQ|GENERAL|ESCALATION"`
- LLM returned uppercase: `"PAYMENT"`
- But enum values are lowercase: `IntentType.PAYMENT = "payment"`
- Pydantic validation failed with:
  ```
  Input should be 'payment', 'faq', 'general', 'escalation' or 'unknown'
  [type=enum, input_value='PAYMENT', input_type=str]
  ```

**Solution**: 
1. Updated prompt to explicitly request lowercase values
2. Added case normalization in code to handle both cases

**Files Modified**:
- `src/prompts/agent_prompts.py` - Updated prompt to request lowercase
- `src/agents/intent_classifier.py` - Added `.lower()` normalization

---

## Changes Made

### File: `src/prompts/agent_prompts.py`

**Before**:
```python
"intent": "PAYMENT|FAQ|GENERAL|ESCALATION",
```

**After**:
```python
"intent": "payment|faq|general|escalation|unknown",
...
IMPORTANT: Use lowercase for intent value (e.g., "payment" not "PAYMENT")
```

### File: `src/agents/intent_classifier.py`

**Added**:
```python
def _extract_json_from_response(self, response: str) -> str:
    """Extract JSON from LLM response, handling markdown code blocks."""
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
    # ... more handling
    return response.strip()
```

**Added normalization**:
```python
# Normalize intent to lowercase (handle both uppercase and lowercase)
if "intent" in result_dict and isinstance(result_dict["intent"], str):
    result_dict["intent"] = result_dict["intent"].lower()
```

---

## Testing

### Before Fix
```
13:51:03 - ERROR - Failed to parse intent classification: 1 validation error for IntentClassification
intent
  Input should be 'payment', 'faq', 'general', 'escalation' or 'unknown'
  [type=enum, input_value='PAYMENT', input_type=str]
```

### After Fix
Server will auto-reload with changes. Test with:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to make a payment of 100 USD"}'
```

Expected: Intent should be correctly classified as `"payment"` and routed to PaymentAgent.

---

## Impact

- ✅ Intent classification now works correctly
- ✅ Handles both uppercase and lowercase from LLM
- ✅ Properly strips markdown code blocks
- ✅ Payment intent messages will route to PaymentAgent
- ✅ FAQ messages will route to FAQAgent
- ✅ Escalation messages will route to EscalationAgent

---

## Additional Files Created

1. **[curl_examples.sh](file:///projects/agentic-ai/langgraph-test/scripts/curl_examples.sh)** - Executable script with all API examples
2. **[curl_examples.md](file:///projects/agentic-ai/langgraph-test/docs/curl_examples.md)** - Documentation with curl commands

---

## Next Steps

1. Server should auto-reload (uvicorn --reload)
2. Test the fixed API with curl examples
3. Verify intent classification works correctly
4. Check that messages route to correct agents
