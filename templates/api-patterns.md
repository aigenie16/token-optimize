# Optimized API Patterns — Anthropic SDK

## Minimal Efficient Request
```python
import anthropic

client = anthropic.Anthropic()

# Haiku for simple tasks
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,  # set tight limit, not default 4096
    messages=[{"role": "user", "content": prompt}]
)
print(response.content[0].text)
```

---

## Prompt Caching — Large Static Context
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": LARGE_STATIC_DOCS_OR_CODEBASE,
        "cache_control": {"type": "ephemeral"}  # ← cache this prefix
    }],
    messages=[{"role": "user", "content": dynamic_question}]
)

# Check savings
usage = response.usage
print(f"Cache read tokens: {usage.cache_read_input_tokens}")
print(f"Cache write tokens: {usage.cache_creation_input_tokens}")
```

---

## Structured JSON Output
```python
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{
        "role": "user",
        "content": f"""
Analyze and return JSON only — no other text:
{{"result": "...", "confidence": 0.0-1.0, "reason": "1 sentence"}}

Input: {input_data}
"""
    }]
)

import json
result = json.loads(response.content[0].text)
```

---

## Batch API — 50% Cost Discount
```python
# Submit batch
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"item-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": item}]
            }
        }
        for i, item in enumerate(items)
    ]
)

# Poll for results (up to 24h)
import time
while batch.processing_status == "in_progress":
    time.sleep(60)
    batch = client.messages.batches.retrieve(batch.id)

for result in client.messages.batches.results(batch.id):
    print(result.custom_id, result.result.message.content[0].text)
```

---

## Streaming — Faster Perceived Response
```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## Token Counter — Pre-flight Check
```python
# Count tokens BEFORE sending (no charge)
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": prompt}]
)
print(f"Input tokens: {token_count.input_tokens}")

# If too high, truncate or summarize before sending
if token_count.input_tokens > 10_000:
    prompt = summarize(prompt)  # your compression function
```

---

## Smart Model Router
```python
def route_model(prompt: str, complexity: str = "auto") -> str:
    """Route to cheapest model that can handle the task."""
    token_count = len(prompt.split()) * 1.3  # rough estimate

    if complexity == "simple" or token_count < 500:
        return "claude-haiku-4-5-20251001"
    elif complexity == "complex" or token_count > 50_000:
        return "claude-opus-4-6"
    else:
        return "claude-sonnet-4-6"

model = route_model(my_prompt)
```

---

## Multi-Turn with Context Compression
```python
MAX_HISTORY_TOKENS = 4000
history = []

def chat(user_message: str) -> str:
    history.append({"role": "user", "content": user_message})

    # Compress history if it's getting long
    history_tokens = sum(len(m["content"].split()) * 1.3 for m in history)
    if history_tokens > MAX_HISTORY_TOKENS:
        summary = summarize_history(history[:-3])  # keep last 3 turns
        history.clear()
        history.append({
            "role": "user",
            "content": f"[Previous context summary: {summary}]"
        })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=history
    )

    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply
```

---

## Cost Calculator
```python
# Prices per 1M tokens (as of 2025)
PRICES = {
    "claude-haiku-4-5-20251001":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-6":          {"input": 3.00,  "output": 15.00},
    "claude-opus-4-6":            {"input": 15.00, "output": 75.00},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICES[model]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000

# Example
cost = estimate_cost("claude-sonnet-4-6", 2000, 500)
print(f"Estimated cost: ${cost:.4f}")
```
