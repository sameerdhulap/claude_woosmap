# Woosmap Project Structure

```
claude_woosmap/
├── README.md                     # Main project documentation
├── STRUCTURE.md                  # This file
├── .gitignore
│
├── skill-tools/                  # Skill Management Utilities
│   ├── init_skill.py             # Initialize new skills
│   ├── package_skill.py          # Package skills for distribution
│   └── README.md
│
├── skills-dist/                  # Distribution
│   ├── woosmap-skill.skill       # Packaged skill (zip archive)
│   ├── INSTALLATION_GUIDE.md     # User installation guide
│   └── README.md
│
└── woosmap-skill/                # Skill Development
    ├── SKILL.md                  # Main skill instructions for Claude
    ├── README.md
    └── scripts/                  # MCP Server
        ├── server.py             # MCP server entry point
        ├── main.py               # Main module
        ├── core.py               # Core utilities
        ├── localities.py         # Places/localities API
        ├── distance.py           # Distance matrix API
        ├── transit.py            # Transit routing API
        ├── exceptions.py         # Custom exceptions
        ├── requirements.txt      # Python dependencies
        ├── pyproject.toml        # Project configuration
        └── README.md
```

## Folder Overview

| Folder | Purpose | Editable |
|--------|---------|----------|
| `skill-tools/` | Python utilities to create and package skills | Yes |
| `skills-dist/` | Packaged `.skill` files for distribution | No (generated) |
| `woosmap-skill/` | Skill instructions + MCP server source code | Yes |

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  woosmap-skill/ │     │     Claude      │     │    scripts/     │
│    (SKILL.md)   │────▶│                 │────▶│  (MCP Server)   │
│   "Knowledge"   │     │   Orchestrates  │     │    "Tools"      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Woosmap API   │
                                                └─────────────────┘
```

- **SKILL.md** = Knowledge (when and how to use the tools)
- **scripts/** = MCP Server (functions that call the Woosmap API)

## Development Workflow

1. **Develop** - Edit `woosmap-skill/SKILL.md` and `woosmap-skill/scripts/`
2. **Test** - Run the MCP server and test with Claude
3. **Package** - Run `python skill-tools/package_skill.py woosmap-skill skills-dist`
4. **Distribute** - Share `skills-dist/woosmap-skill.skill`

## MCP Server Modules

| Module | Description |
|--------|-------------|
| `server.py` | MCP server setup and entry point |
| `localities.py` | Place search, autocomplete, geocoding |
| `distance.py` | Distance matrix calculations |
| `transit.py` | Public transit routing |
| `core.py` | Shared utilities and helpers |
| `exceptions.py` | Custom error handling |
