# Token Optimization — Deep Techniques

---

## 1. Prompt Compression

### Principle
Every token that doesn't change Claude's output should be cut.

### Compression Steps
1. **Identify task** — what is the one thing you need?
2. **Identify constraints** — format, length, scope
3. **Remove filler** — greetings, apologies, hedging
4. **Replace prose with structure** — bullet > paragraph
5. **Use implicit context** — Claude knows common patterns

### Before / After Examples

**Before (47 tokens):**
> "Hello! I hope you're doing well. I was wondering if you could help me understand what the useState hook does in React and how I should use it?"

**After (13 tokens):**
> "Explain React useState. [2 sentences, senior dev level]"

**Before (89 tokens):**
> "I have a bug in my code. I've been working on this for a while. The error message says 'Cannot read property of undefined'. It happens when I click the submit button. Here is my function: [code]"

**After (28 tokens + code):**
> "Bug: 'Cannot read property of undefined' on submit click. [code] Fix only. [DIFF]"

---

## 2. Response Format Control

### Always specify what you want back
Unguided responses are 2–5x longer than needed.

```
# Length control
"Answer in ≤ [N] words / sentences / bullets"
"One paragraph max"

# Format control
"Return JSON: {field1, field2}"
"Markdown table: cols [A, B, C]"
"Unified diff only"
"Code block only, no explanation"

# Scope control
"Issues only — no praise, no suggestions"
"Changed lines only, not full file"
"Top 3 only"
"Most important point only"
```

### Format tokens comparison (same information)
| Format | Tokens |
|--------|--------|
| Prose paragraph | ~120 |
| Bullet list | ~60 |
| JSON object | ~40 |
| Single value | ~5 |

---

## 3. Prompt Caching (Anthropic API)

### How it works
- Cache prefix: min 1024 tokens (Sonnet/Opus) / 2048 tokens (Haiku)
- Cached tokens cost 10% of normal input price
- Cache lifetime: 5 minutes (refreshed on each use)
- Write cost: 25% extra on first cache write

### Optimal structure
```
[SYSTEM - static, long]          ← cache_control: ephemeral
  Project context / docs
  Tool definitions
  Few-shot examples

[USER turn 1 - dynamic]          ← NOT cached
  Actual question

[ASSISTANT turn 1]
[USER turn 2 - dynamic]          ← prefix cached, question new
```

### Implementation (Python SDK)
```python
client.messages.create(
    model="claude-sonnet-4-6",
    system=[{
        "type": "text",
        "text": YOUR_LARGE_STATIC_CONTEXT,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": user_question}]
)
```

### In Claude Code / daily use
- Keep the same session open → context prefix is cached
- Don't /clear between related questions
- CLAUDE.md content is loaded once and cached

---

## 4. Context Pruning

### What to cut from context
```
✂ Earlier debug attempts that didn't work
✂ Brainstorming that led nowhere
✂ Verbose explanations you already understood
✂ Full file contents when only one function matters
✂ Error messages older than the current bug
```

### Summarization pattern
When a conversation gets long:
```
"Summary of what we've established:
- [fact 1]
- [fact 2]
- Current state: [X]
Next: [task]"
```
This summary replaces 1000+ tokens of history with ~100.

### Reference pattern
Instead of re-pasting code:
```
"Same function as above — now also handle [edge case]"
"Add to the JSON structure from turn 3"
"Fix the issue but keep the auth logic unchanged"
```

---

## 5. Code-Specific Optimization

### Diff-based updates
```
❌ "Here's my full 300-line file. Rewrite it with X added."
✅ "Add X to [function name] at line 45. Return diff only."
```

### Targeted extraction
```
❌ "Here's my repo. Where's the bug?"
✅ "Bug in auth flow. Relevant code: [20-line excerpt].
    file: src/auth/middleware.ts:34-54"
```

### Code review efficiency
```
❌ "Review this code" (gets everything)
✅ "Review for: security issues only"
✅ "Review for: performance bottlenecks, return top 3"
✅ "Does this follow SOLID? Yes/No + 1 sentence each"
```

---

## 6. Multi-Turn Efficiency

### Batch your questions
One round-trip is always better than many.

```
"Three questions:
1. [Q1]
2. [Q2]
3. [Q3]
[SHORT] label each answer 1/2/3"
```

### Chain-of-thought: only when needed
Extended thinking and "think step by step" adds tokens.
Only use for:
- Complex math / logic
- Multi-constraint optimization
- Novel reasoning

Skip for:
- Lookups / recall
- Simple transformations
- Pattern matching

### Iterative refinement vs. one-shot
```
❌ Sending incomplete prompt → getting wrong answer → correcting → repeat
✅ Spend 30 seconds writing a precise prompt → get right answer in 1 shot
```
Each correction round costs 2x the tokens of the original.

---

## 7. System Prompt Optimization

### Principles
1. State rules, not reasoning (saves 50–70%)
2. Use lists, not paragraphs
3. Remove redundant constraints
4. Define output format once explicitly

### Before (~200 tokens):
> "You are a helpful assistant that always tries to be concise and clear. When someone asks you a question, please make sure to think carefully before answering and provide a well-structured response. You should always be polite and professional in your responses and avoid using overly technical jargon unless the user is clearly technical..."

### After (~50 tokens):
> "Assistant rules: concise, professional. Match technical level to user. Format: bullets for lists, code blocks for code. Skip preamble."

---

## 8. Model Routing

### Decision tree
```
Is the task creative/complex/long-context (>100k)?
  YES → claude-opus-4-6

Is it standard dev work, analysis, writing?
  YES → claude-sonnet-4-6 (default)

Is it simple: classify, summarize, translate, format?
  YES → claude-haiku-4-5
```

### Cost impact
A team doing 1000 API calls/day:
- All Opus: $$$
- Smart routing (70% Haiku, 25% Sonnet, 5% Opus): ~85% cost reduction

---

## 9. Structured Output (JSON Mode)

Request structured output to eliminate parsing and trim prose:

```python
# API
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": f"""
        Analyze this code for issues.
        Return JSON only:
        {{"issues": [{{"line": int, "severity": "high|med|low", "fix": "string"}}]}}

        Code: {code}
    """}]
)
```

Benefits:
- 40–60% fewer output tokens (no prose wrapping)
- No parsing needed
- Predictable structure

---

## 10. Batch API (Non-Urgent Tasks)

For tasks that don't need immediate response:
- 50% cost discount
- Up to 24-hour turnaround
- Perfect for: nightly reports, bulk analysis, offline processing

```python
batch = client.messages.batches.create(
    requests=[
        {"custom_id": f"item-{i}",
         "params": {"model": "claude-haiku-4-5", "messages": [...]}}
        for i, item in enumerate(items)
    ]
)
```
