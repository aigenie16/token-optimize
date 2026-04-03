# Token Optimization — Daily Use System

> Maximum token savings. Zero quality loss.

---

## What's in this repo

| File | Purpose |
|------|---------|
| `SKILL.md` | Claude Code skill — load this as a plugin skill |
| `CHEATSHEET.md` | Quick daily reference card |
| `TECHNIQUES.md` | Deep-dive on every technique |
| `templates/` | Ready-to-use optimized prompt templates |

---

## Install (30 seconds)

```bash
git clone https://github.com/YOUR_USERNAME/token-optimize
cd token-optimize
bash install.sh
```

Restart Claude Code → type `/token-optimize` → done.

**Requirement:** [Claude Code](https://claude.ai/code) must be installed.

---

## Quick Start

**3 rules that cover 80% of savings:**

1. **Send only what Claude needs** — no preamble, no context it already has
2. **Demand short output** — add `[CONCISE]` or specify exact format
3. **Use static-first ordering** — put stable content before dynamic content (cache hits)

---

## Estimated Savings by Technique

| Technique | Avg Token Reduction |
|-----------|-------------------|
| Prompt compression | 30–50% input |
| Response format control | 40–60% output |
| Prompt caching (Anthropic) | Up to 90% on cached prefix |
| Model routing (Haiku for simple) | 80% cost reduction |
| Context pruning | 20–40% input |
| Diff-based code updates | 60–80% input (code tasks) |

---

## Model Selection Guide

```
Simple Q&A / classification / formatting  →  claude-haiku-4-5
Standard coding / analysis / writing      →  claude-sonnet-4-6  (default)
Complex reasoning / long context          →  claude-opus-4-6
```

Cost ratio: Haiku : Sonnet : Opus ≈ 1 : 5 : 25
