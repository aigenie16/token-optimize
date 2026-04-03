#!/usr/bin/env python3
"""
Token Optimizer — compress prompts before sending to Claude API.
Usage:
    python token_optimizer.py "your prompt here"
    python token_optimizer.py --file prompt.txt
    python token_optimizer.py --interactive
"""

import re
import sys
import argparse
from typing import Optional

# ─── Filler patterns to strip ────────────────────────────────────────────────

FILLER_PHRASES = [
    # Greetings
    r"(?i)^(hi|hello|hey)[!,.]?\s*",
    # Hope phrases
    r"(?i)i hope you'?re doing well[,.]?\s*",
    r"(?i)i hope (this finds|this helps) you[,.]?\s*",
    # Wondering/asking intros
    r"(?i)i was wondering if (you could |you can )?",
    r"(?i)i wanted to (ask|know|understand) (if |whether )?(you could |you can )?",
    r"(?i)i would( like to| love to)? (know|understand|ask)",
    r"(?i)could you (please |kindly )?(help me )?(with |understand |explain )?",
    r"(?i)can you (please |kindly )?(help me )?(with |understand |explain )?",
    # Context padding
    r"(?i)i'?ve been (working on|stuck on|thinking about) this (for a while|for some time)[,.]?\s*",
    r"(?i)i'?m not (very |that )?familiar with [^.]+[.!]?\s*",
    r"(?i)i'?m new to [^.]+[.!]?\s*",
    r"(?i)i'?ve been (having|getting) (this |an )?issue (for a while|for some time)[,.]?\s*",
    # AI self-references
    r"(?i)as an ai( language model)?,?\s*",
    r"(?i)as a large language model,?\s*",
    # Trailing closers
    r"(?i)thank(s| you)( (in advance|so much|very much))?[!.]?\s*$",
    r"(?i)i hope this (makes sense|is clear|is helpful)[!.]?\s*$",
    r"(?i)let me know if you need (any )?more (information|context|details)[!.]?\s*$",
    r"(?i)feel free to ask (if )?you have (any )?questions[!.]?\s*$",
    r"(?i)any help (would be|is) (appreciated|great|helpful)[!.]?\s*$",
    r"(?i)please (help|assist) me[.!]?\s*$",
]

FILLER_WORDS = [
    "basically", "essentially", "literally", "actually", "honestly",
    "obviously", "clearly", "certainly", "definitely", "absolutely",
    "just", "simply", "really", "very", "quite", "rather",
]

# ─── Format directives ────────────────────────────────────────────────────────

FORMAT_DIRECTIVES = {
    "code": "[CODE]",
    "diff": "[DIFF]",
    "bullets": "[BULLETS]",
    "json": "[JSON]",
    "table": "[TABLE]",
    "short": "[SHORT]",
    "concise": "[CONCISE]",
    "no-intro": "[NO-INTRO]",
}

# ─── Model routing ────────────────────────────────────────────────────────────

SIMPLE_KEYWORDS = [
    "translate", "convert", "format", "fix typo", "summarize briefly",
    "classify", "yes or no", "true or false", "which is correct",
    "sort", "list", "rename", "what is", "define",
]

COMPLEX_KEYWORDS = [
    "architect", "design system", "analyze entire", "comprehensive",
    "100k", "long document", "full codebase", "complex reasoning",
    "multi-step", "trade-offs", "evaluate all",
]


def count_tokens(text: str) -> int:
    """Rough token estimate: ~1.3 tokens per word."""
    return int(len(text.split()) * 1.3)


def strip_filler(text: str) -> str:
    """Remove filler phrases and words."""
    result = text.strip()

    # Iteratively strip filler (some patterns expose others)
    for _ in range(3):
        for pattern in FILLER_PHRASES:
            result = re.sub(pattern, " ", result).strip()

    # Normalize whitespace
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = re.sub(r" {2,}", " ", result)

    # Fix orphaned conjunctions at start: "and X", "or X"
    result = re.sub(r"(?i)^(and|or|but|so)\s+", "", result).strip()

    return result.strip()


def detect_missing_format(text: str) -> list[str]:
    """Detect when a format directive would help."""
    suggestions = []

    lower = text.lower()

    if any(w in lower for w in ["code", "function", "script", "implement", "write"]):
        if "[code]" not in lower and "[diff]" not in lower:
            suggestions.append("Add [CODE] to get code-only output")

    if any(w in lower for w in ["fix", "change", "update", "modify", "edit"]):
        if "[diff]" not in lower:
            suggestions.append("Add [DIFF] to get only changed lines")

    if any(w in lower for w in ["list", "options", "steps", "points"]):
        if "[bullets]" not in lower and "[table]" not in lower:
            suggestions.append("Add [BULLETS] or [TABLE] to structure output")

    if any(w in lower for w in ["explain", "what is", "how does", "describe"]):
        if not re.search(r"\d+ (sentence|word|line|paragraph)", lower):
            suggestions.append("Add length constraint e.g. '[2 sentences]' or '[SHORT]'")

    if len(text.split("?")) > 3:
        suggestions.append("Multiple questions detected — batch with Q1/Q2/Q3 labels")

    return suggestions


def recommend_model(text: str) -> tuple[str, str]:
    """Return (model_id, reason)."""
    lower = text.lower()
    tokens = count_tokens(text)

    if tokens > 50_000 or any(k in lower for k in COMPLEX_KEYWORDS):
        return "claude-opus-4-6", "complex task or long context"

    if any(k in lower for k in SIMPLE_KEYWORDS) or tokens < 100:
        return "claude-haiku-4-5-20251001", "simple task — 80% cheaper"

    return "claude-sonnet-4-6", "standard task"


def optimize_prompt(prompt: str, verbose: bool = True) -> dict:
    """
    Analyze and optimize a prompt.
    Returns dict with original, optimized, tokens, savings, suggestions.
    """
    original_tokens = count_tokens(prompt)

    # Apply compression
    optimized = strip_filler(prompt)

    optimized_tokens = count_tokens(optimized)
    savings_pct = round((1 - optimized_tokens / original_tokens) * 100) if original_tokens > 0 else 0

    # Detect format opportunities
    suggestions = detect_missing_format(optimized)

    # Model recommendation
    model, model_reason = recommend_model(optimized)

    result = {
        "original": prompt,
        "optimized": optimized,
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "savings_pct": savings_pct,
        "suggestions": suggestions,
        "recommended_model": model,
        "model_reason": model_reason,
    }

    if verbose:
        _print_result(result)

    return result


def _print_result(r: dict) -> None:
    """Pretty-print optimization result."""
    print("\n" + "═" * 60)
    print("TOKEN OPTIMIZER RESULT")
    print("═" * 60)
    print(f"\nORIGINAL:  ~{r['original_tokens']} tokens")
    print(f"OPTIMIZED: ~{r['optimized_tokens']} tokens")
    print(f"SAVINGS:   ~{r['savings_pct']}%")
    print(f"\nMODEL: {r['recommended_model']} ({r['model_reason']})")

    if r["suggestions"]:
        print("\nSUGGESTIONS:")
        for s in r["suggestions"]:
            print(f"  • {s}")

    print("\nOPTIMIZED PROMPT:")
    print("─" * 60)
    print(r["optimized"])
    print("─" * 60)

    if r["savings_pct"] < 10:
        print("\n✓ Already efficient. Consider adding format directives.")


def interactive_mode() -> None:
    """Run optimizer in interactive mode."""
    print("Token Optimizer — Interactive Mode")
    print("Paste your prompt (type END on a new line to submit, Ctrl+C to quit)\n")

    while True:
        try:
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)

            prompt = "\n".join(lines)
            if prompt.strip():
                optimize_prompt(prompt)
            print("\n" + "─" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nBye!")
            break


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize prompts for maximum token efficiency"
    )
    parser.add_argument("prompt", nargs="?", help="Prompt text to optimize")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Output optimized prompt only")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    prompt = None

    if args.file:
        with open(args.file) as f:
            prompt = f.read()
    elif args.prompt:
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    result = optimize_prompt(prompt, verbose=not args.quiet)

    if args.quiet:
        print(result["optimized"])


if __name__ == "__main__":
    main()
