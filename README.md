# Claude Woosmap Project

This repository contains the Woosmap MCP server and Claude skill for geolocation and mapping services.

## Folder Structure

```
claude/
├── woosmap/                    # Woosmap MCP Server
│   ├── server.py              # MCP server implementation
│   ├── requirements.txt       # Python dependencies
│   └── ...                    # Other server files
│
├── woosmap-skill/             # Skill Development Folder
│   ├── SKILL.md              # Main skill instructions for Claude
│   └── README.md             # Development documentation
│
└── skills-dist/               # Packaged Skills for Distribution
    ├── woosmap.skill         # Distributable skill package
    └── README.md             # Installation instructions
```

## Components

### 1. Woosmap MCP Server (`woosmap/`)
The Model Context Protocol (MCP) server that connects to the Woosmap API and provides tools for:
- Place search and autocomplete
- Geocoding and reverse geocoding
- Route calculation and navigation
- Distance matrix computation
- Toll cost calculation
- Public transit routing

**Setup**: See `woosmap/README.md` for installation and configuration.

### 2. Woosmap Skill (`woosmap-skill/`)
Development folder for the Claude skill that teaches Claude when and how to use the Woosmap MCP tools effectively.

**Purpose**: Provides Claude with:
- Triggering logic (when to use Woosmap)
- Workflow guidance (how to chain API calls)
- Parameter best practices
- Common usage patterns

**Development**: See `woosmap-skill/README.md` for editing and testing.

### 3. Distribution (`skills-dist/`)
Contains packaged `.skill` files ready for distribution to end users.

**Usage**: See `skills-dist/README.md` for installation instructions.

## Quick Start

### For Developers

1. **Set up the MCP server**:
   ```bash
   cd woosmap
   pip install -r requirements.txt
   # or using uv:
   uv sync
   # Configure your Woosmap API key
   ```

2. **Edit the skill** (optional):
   ```bash
   cd woosmap-skill
   # Edit SKILL.md as needed
   ```

3. **Package the skill**:
   ```bash
   python3 /path/to/skill-creator/scripts/package_skill.py woosmap-skill skills-dist
   ```

### For End Users

1. **Install the MCP server** (follow woosmap/ documentation)
2. **Install the skill**:
   ```bash
   unzip skills-dist/woosmap.skill -d ~/.claude/skills/
   ```
3. **Configure Claude** to use both MCP and skill

## How It Works

```
User Query: "Find coffee shops near me"
      ↓
Claude reads the skill (woosmap-skill/SKILL.md)
      ↓
Claude knows to use: autocomplete_localities
      ↓
Claude calls the MCP server (woosmap/)
      ↓
MCP server queries Woosmap API
      ↓
Results returned to Claude
      ↓
Claude formats response for user
```

## Requirements

- **Python 3.8+** for MCP server
- **Woosmap API Key** (get from https://developers.woosmap.com/)
- **Claude** (Sonnet 4 or later recommended)
- **MCP-compatible Claude interface** (Claude.ai, API, etc.)

## Development Workflow

1. **Develop**: Edit files in `woosmap-skill/`
2. **Test**: Use Claude to test the skill with real queries
3. **Package**: Create `.skill` file in `skills-dist/`
4. **Distribute**: Share the `.skill` file

## Documentation

- [Woosmap API Docs](https://developers.woosmap.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Claude Skills Guide](https://docs.anthropic.com/)

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues:
- **MCP Server**: Check `woosmap/` documentation
- **Skill**: Check `woosmap-skill/` documentation
- **Woosmap API**: Visit https://developers.woosmap.com/support
