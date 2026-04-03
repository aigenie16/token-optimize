#!/bin/bash
# Token Optimize — Claude Code Skill Installer

echo "Installing token-optimize skill for Claude Code..."

# Create directories
mkdir -p ~/.claude/skills/token-optimize
mkdir -p ~/.claude/commands

# Copy skill
cp "$(dirname "$0")/SKILL.md" ~/.claude/skills/token-optimize/SKILL.md

# Copy slash command
cp "$(dirname "$0")/templates/token-optimize-command.md" ~/.claude/commands/token-optimize.md

echo "Done! Restart Claude Code and use /token-optimize"
