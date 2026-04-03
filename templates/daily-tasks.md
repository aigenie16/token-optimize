# Optimized Templates — Daily Dev Tasks

Copy-paste these. Fill in [brackets]. Delete unused lines.

---

## CODE TASKS

### Fix a Bug
```
Bug: [error message or description]
File: [path:line]
[paste only the broken function/block — NOT the full file]
Fix only. [DIFF]
```

### Add a Feature
```
Add [feature] to [function/component name] in [file:line].
Constraint: [minimal change / no new dependencies / etc]
[Code block only]
```

### Refactor
```
Refactor [function] for [goal: readability / performance / testability].
Keep: [what must not change]
Return: diff only.
```

### Code Review
```
Review [paste excerpt OR file:line range].
Focus: [security / performance / correctness / style]
Output: issues only, severity (H/M/L), 1-line fix per issue. [TABLE]
```

### Explain Code
```
Explain [paste short excerpt or function name].
Audience: [junior dev / senior dev / non-technical]
[2 sentences / bullet list]
```

### Write Tests
```
Write [unit / integration] tests for [function name].
File: [path]
Framework: [Jest / Pytest / etc]
Cover: happy path + [N] edge cases. Code only.
```

### Debug
```
Error: [exact error + stack trace top 5 lines]
Context: [what triggers it, what I tried]
[paste minimal reproducing code]
Root cause + fix. [CONCISE]
```

---

## ANALYSIS TASKS

### Compare Options
```
Compare [A] vs [B] for [use case].
Criteria: [speed / cost / dx / scalability]
Format: table. Recommendation: 1 sentence.
```

### Architecture Review
```
Review this architecture for [goal].
[paste diagram description or brief]
Issues: top 3 only. [BULLETS]
```

### Performance Analysis
```
Analyze [function/query] for performance.
[paste code]
Output: bottlenecks + fix per bottleneck. No explanation needed.
```

---

## WRITING TASKS

### Write Docs
```
Write [JSDoc / README section / API doc] for:
[paste function signature or describe endpoint]
[CONCISE]. Include: params, returns, example. Code format.
```

### Write Commit Message
```
Write commit message for:
[paste diff or describe change]
Format: conventional commits. 1 subject line + optional body bullets.
```

### Write PR Description
```
PR: [feature/fix name]
Changes: [2–3 bullet summary]
Write: title + body with Summary and Test plan sections. [CONCISE]
```

### Summarize
```
Summarize [document/article/thread]:
[paste content]
Output: TL;DR (1 sentence) + key points (≤5 bullets).
```

---

## QUICK ONE-LINERS

```
"Convert [code] to [language]. Code only."
"Rename [X] to [Y] throughout. Return diff."
"Add types to [function]. TypeScript. Inline only."
"SQL: [describe query]. Return query only."
"Regex for [pattern]. Return pattern + 2 test examples."
"Shell command to [task]. One-liner."
"JSON schema for [describe structure]."
"Fix indentation/formatting. Code only."
```

---

## BATCH QUESTION TEMPLATE

```
Three questions, answer [SHORT] and label:
Q1: [question]
Q2: [question]
Q3: [question]
```

---

## CLAUDE CODE SESSION STARTERS

```
# For a new task (clean context):
/clear
[your optimized prompt]

# For continuing work:
"Continuing from above — now [next step]"

# For project-wide context:
(Put in CLAUDE.md — loaded automatically, not re-sent each turn)
```
