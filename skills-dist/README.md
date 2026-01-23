# Woosmap Skill - Distribution

This folder contains packaged Woosmap skills ready for distribution and installation.

## Files

- **woosmap-skill.skill** - Packaged skill file (zip archive with .skill extension)

## What is a .skill file?

A `.skill` file is a zip archive containing:
- SKILL.md with instructions for Claude
- Optional scripts, references, and assets

## Installation

### For End Users

1. **Download** the `woosmap-skill.skill` file
2. **Extract** to your Claude skills directory:
   ```bash
   # Extract the skill
   unzip woosmap-skill.skill -d /path/to/claude/skills/user/
   ```
3. **Configure** Claude to recognize the skill (if needed)

### For Claude.ai Users

If Claude.ai supports skill uploads:
1. Upload `woosmap-skill.skill` through the skills interface
2. The skill will automatically be available

## Prerequisites

Before using this skill, you must have:

1. **Woosmap MCP Server** installed and running
2. **Woosmap API Key** configured
3. **Claude** configured to connect to the MCP server

## What This Skill Does

The Woosmap skill teaches Claude:
- When to use Woosmap tools (place search, routing, geocoding)
- How to structure API calls with proper parameters
- Best practices for location-based queries
- Common workflows (finding places, getting directions, etc.)

## Version

- **Version**: 1.0.0
- **Created**: January 2026
- **Compatible with**: Claude Sonnet 4.5 and later

## Support

For issues or questions:
- Woosmap API: https://developers.woosmap.com/
- Skill development: See `../woosmap-skill/README.md`

## Updating the Skill

To update this packaged skill:

1. Edit files in `../woosmap-skill/`
2. Run the packaging script:
   ```bash
   # From the project root (claude_woosmap/)
   python3 skill-tools/package_skill.py woosmap-skill skills-dist
   ```
3. The updated `woosmap-skill.skill` will be created here
