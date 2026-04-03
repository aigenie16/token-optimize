# Token Optimizer Skill

## Purpose
Compress, restructure, and optimize any prompt or workflow to minimize token usage without losing quality, accuracy, or output value.

**Triggers:**
- "optimize this prompt"
- "compress this"
- "make this token-efficient"
- "reduce tokens"
- "how do I ask this better"
- `/token-optimize` or `/to`

---

## Skill Execution

When triggered, Claude should:

### Step 1 — Analyze the input
Identify:
- Filler words and phrases (remove)
- Repeated context (collapse to reference)
- Format inefficiency (prose → structure)
- Overly broad scope (narrow to essentials)
- Missing output constraints (add format directives)

### Step 2 — Apply these transformations in order

**A. Strip filler**
Remove: greetings, apologies, hedging, "as an AI", "please", "I was wondering", "can you help me", praise, closing remarks.

**B. Compress to minimum viable context**
- Cut any context that doesn't change Claude's answer
- Replace paragraph explanation with 1-line fact
- Replace full file with relevant excerpt + path:line reference
- Collapse repetition with "same as above" / reference

**C. Add output format directives**
Choose the tightest format that still carries the information:
- `[CODE]` — code only, no prose
- `[DIFF]` — changed lines only
- `[JSON: {fields}]` — structured output
- `[BULLETS]` — list, no paragraphs
- `[TABLE: cols]` — tabular
- `[SHORT]` — ≤3 sentences
- `[1-LINER]` — single line
- `[N words max]` — hard limit
- `[NO-INTRO]` — skip preamble

**D. Route to correct model**
Recommend model based on task:
- Simple / classify / format → `haiku`
- Standard dev / writing / analysis → `sonnet` (default)
- Complex reasoning / long context → `opus`

**E. Add caching hint if applicable**
If the user has a large static context (docs, codebase, system prompt) that repeats across calls, note:
> "Cache this prefix: add `cache_control: {"type": "ephemeral"}` — saves 90% on repeat calls"

### Step 3 — Output

Return:
```
ORIGINAL TOKENS: ~[estimate]
OPTIMIZED TOKENS: ~[estimate]
SAVINGS: ~[%]

OPTIMIZED PROMPT:
---
[the compressed, precise prompt]
---

DIRECTIVES ADDED: [list what was added and why]
MODEL: [recommended model]
```

---

## Quick Compression Rules (apply always)

| Rule | Example |
|------|---------|
| Task first, context second | "Fix bug: [code]" not "I have some code with a bug..." |
| Structure > prose | bullets, JSON, tables |
| Format directive at end | `[CODE]` `[DIFF]` `[JSON]` |
| Scope the output | "top 3 only" "issues only" "1 sentence" |
| Reference don't repeat | "same function as above" |
| Batch questions | Q1/Q2/Q3 in one message |
| Cut file to excerpt | path:line, not full file |

---

## Example Transformations

### Example 1 — Bug Fix

**Original (67 tokens):**
> "Hi! I hope you can help me. I'm having an issue with my React application. I get this error: 'Cannot read property map of undefined'. It happens when the component loads. I've been stuck on this for a while. Can you help me figure out what's wrong? Here is my component code: [500 lines]"

**Optimized (18 tokens + code):**
> "Bug: 'Cannot read property map of undefined' on mount.
> [paste only the 20-line component, not 500 lines]
> Fix. [CODE]"

**Savings: 73% input, 60% output**

---

### Example 2 — Code Review

**Original (38 tokens):**
> "Could you please review my code and let me know if there are any issues, suggestions for improvement, or anything I might be doing wrong?"

**Optimized (14 tokens):**
> "Review [excerpt]. Issues only, severity H/M/L, 1-line fix each. [TABLE]"

**Savings: 63% input, 70% output**

---

### Example 3 — Explanation

**Original (29 tokens):**
> "I'm not very familiar with this concept. Could you explain to me what React's useEffect hook does and when I should use it?"

**Optimized (10 tokens):**
> "Explain useEffect: what + when. [2 sentences, senior dev level]"

**Savings: 66% input, 65% output**

---

### Example 4 — Multi-question (Batching)

**Original (3 separate messages, 3 round-trips):**
> Turn 1: "What's the difference between == and === in JS?"
> Turn 2: "When should I use const vs let?"
> Turn 3: "What does the spread operator do?"

**Optimized (1 message, 1 round-trip):**
> "Q1: == vs === in JS? Q2: const vs let — when each? Q3: spread operator?
> [SHORT] label Q1/Q2/Q3"

**Savings: 67% fewer round-trips + 50% token reduction**

---

## CLAUDE.md Template (project-level token optimization)

Add to your project's CLAUDE.md to set defaults once:

```markdown
# Response Defaults
- Be concise. Skip preamble and closing remarks.
- Code tasks: return code only unless explanation asked.
- Use diffs for edits, not full file rewrites.
- Bullet points over paragraphs.
- Ask clarifying questions only if the task is genuinely ambiguous.

# Project Context (so I don't have to repeat it)
- Stack: [your stack]
- Conventions: [key conventions]
- Don't: [what to avoid]
```

---

## Anti-Patterns to Flag

When analyzing a user's prompt, flag these explicitly:

1. **Full file paste** → "Only paste the relevant function (lines X–Y)"
2. **No output format** → "Add [CODE] / [BULLETS] / [JSON] to control output"
3. **Repeated project context** → "Move this to CLAUDE.md"
4. **Chain of single questions** → "Batch into one message"
5. **Opus for simple task** → "Use Haiku — 80% cheaper"
6. **No max_tokens set** (API) → "Set max_tokens to avoid runaway output"
7. **Prose system prompt** → "Convert to bullet rules — 50% shorter"
