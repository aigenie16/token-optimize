# Token Optimization — Daily Cheatsheet

---

## INPUT COMPRESSION RULES

### Remove these — they add zero value
```
❌ "Can you please help me with..."
❌ "I was wondering if you could..."
❌ "Thank you in advance for..."
❌ "As an AI language model..."
❌ "I hope this makes sense"
❌ Long backstory Claude doesn't need

✅ Go straight to the task
```

### Shorthand Directives (put at END of prompt)
```
[SHORT]       — response under 3 sentences
[BULLETS]     — bullet list only, no prose
[CODE]        — code only, no explanation
[DIFF]        — show only changed lines
[JSON]        — return valid JSON only
[TABLE]       — tabular format
[1-LINER]     — single line answer
[NO-INTRO]    — skip preamble/summary
[STEP-BY-STEP] — numbered steps only
[CONCISE]     — be maximally brief
```

### Context Reduction
```
Instead of pasting full file (500 lines):
  → Paste only the relevant function/section
  → Add: "file: src/auth/login.ts:45-80"

Instead of explaining project background:
  → "React + TypeScript app, standard CRA setup"

Instead of repeating earlier messages:
  → "same context as above" or reference by [#turn]
```

### Code Task Shortcuts
```
Bug fix:     "Bug: [error]. File: [path:line]. Fix only."
Refactor:    "Refactor [function] for [goal]. Return diff only."
Review:      "Review [file excerpt]. Issues only, no praise."
Explain:     "Explain [concept] in 2 sentences for a senior dev."
Add feature: "Add [feature] to [function]. Minimal code change."
```

---

## OUTPUT CONTROL DIRECTIVES

### Response Length
```
"Answer in ≤50 words"
"Max 3 bullet points"
"One paragraph only"
"Return only the code block"
"TL;DR first, then details if needed"
```

### Format Requests
```
"Return as JSON: {key, value, reason}"
"Format as markdown table: columns [A, B, C]"
"Return only changed lines as unified diff"
"Output: filename + code block only"
```

### Exclude Boilerplate
```
"Skip: intro, explanation, closing remarks"
"No comments in code"
"No type annotations"
"Omit error handling (I'll add it)"
```

---

## PROMPT CACHING (Anthropic API)

**Rule:** Stable content FIRST, dynamic content LAST.

```
system prompt (static, never changes)
  + reference docs / code base context (semi-static)
    + few-shot examples (static)
      → user message (dynamic, changes each turn)
```

Cache kicks in after 1024 tokens. Saves 90% cost on cached prefix.

Add `cache_control: {"type": "ephemeral"}` on large static blocks.

**In Claude Code:** Reuse the same session — context is cached automatically.

---

## CONTEXT WINDOW MANAGEMENT

```
Start fresh for unrelated tasks     — don't carry stale context
Summarize before long continuations — "Summary so far: ..."
Use /clear in Claude Code           — wipes context, starts fresh
Reference files by path             — don't paste full contents
```

---

## MODEL ROUTING HEURISTIC

```python
if task in [classify, format, translate, simple_qa]:
    use("haiku")          # 80% cheaper
elif task in [code, analysis, writing, multi_step]:
    use("sonnet")         # balanced
elif task in [complex_reasoning, >100k_context, creative]:
    use("opus")           # max capability
```

---

## ANTI-PATTERNS (tokens wasted daily)

| Anti-Pattern | Fix |
|-------------|-----|
| Pasting entire files | Paste only relevant section |
| Asking Claude to "think step by step" when not needed | Drop it for simple tasks |
| Repeating context from prior turns | Reference or summarize |
| Getting long explanations you'll skim | Add `[CODE]` or `[BULLETS]` |
| Using Opus for simple tasks | Route to Haiku |
| Asking one question per message | Batch related questions |
| Not using prompt caching for static docs | Set cache_control |
| Re-explaining your project every session | Use CLAUDE.md |

---

## BATCH QUESTIONS (1 round-trip vs many)

```
❌ Three separate messages:
"What does X do?"
"How do I fix Y?"
"Should I use Z or W?"

✅ One message:
"Q1: What does X do? Q2: Fix for Y? Q3: Z vs W — which for [use case]?
[SHORT] answer each, label Q1/Q2/Q3"
```

---

## CLAUDE CODE SPECIFIC

```
Use CLAUDE.md         — project context loaded once, not re-sent
Use /compact          — compresses conversation history
Use /clear            — fresh context for new task
Glob/Grep > Read      — search before loading full files
Specific file:line    — don't ask Claude to search, point directly
```
