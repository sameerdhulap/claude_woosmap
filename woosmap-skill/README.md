# Woosmap Skill - Development

This folder contains the Woosmap skill in development/editable format.

## Structure

```
woosmap-skill/
└── SKILL.md              # Main skill file with instructions for Claude
```

## What is this skill?

This skill teaches Claude when and how to use the Woosmap MCP server tools for:
- Searching for places and addresses
- Finding nearby locations
- Getting directions and routes
- Geocoding and reverse geocoding
- Calculating distances and travel times
- Computing toll costs
- Planning public transit routes

## Development Workflow

1. **Edit**: Modify `SKILL.md` to update instructions
2. **Test**: Use Claude to test the skill with real queries
3. **Package**: Run the packaging script to create distributable `.skill` file
4. **Distribute**: Share the packaged `.skill` file with others

## Packaging the Skill

To create a distributable `.skill` file:

```bash
# From the parent directory
python3 /path/to/skill-creator/scripts/package_skill.py woosmap-skill skills-dist
```

This will validate the skill and create `skills-dist/woosmap.skill`.

## Optional Additions

You can add these folders if needed:

- **scripts/**: Executable helper scripts (Python, Bash, etc.)
- **references/**: Additional documentation or API references
- **assets/**: Templates, images, or other resources

## Relationship to MCP Server

- **MCP Server** (`../woosmap/`): The actual Woosmap API service
- **This Skill**: Instructions for Claude on how to use the MCP tools

The skill doesn't contain the MCP server code - it only provides guidance for Claude.
