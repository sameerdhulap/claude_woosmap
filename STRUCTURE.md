# Woosmap Project Structure

```
/******/claude/
│
├── README.md                           # Main project documentation
│
├── woosmap/                           # MCP Server (your existing folder)
│   ├── server.py                      # MCP server implementation
│   ├── mcp_config.json                # MCP configuration
│   ├── requirements.txt               # Python dependencies
│   └── ...                            # Other server files
│
├── woosmap-skill/                     # Skill Development (NEWLY CREATED)
│   ├── SKILL.md                       # Main skill file for Claude
│   └── README.md                      # Development guide
│
└── skills-dist/                       # Distribution (NEWLY CREATED)
    ├── woosmap.skill                  # Packaged skill (zip archive)
    └── README.md                      # Installation guide
```

## What Each Folder Does

### woosmap/ (MCP Server)
- **Purpose**: The actual service that talks to Woosmap API
- **Technology**: Python MCP server
- **Used by**: Claude (via MCP protocol)
- **Contains**: API client code, server logic, configuration

### woosmap-skill/ (Development)
- **Purpose**: Teaches Claude how to use the MCP tools
- **Technology**: Markdown documentation
- **Used by**: Claude (reads SKILL.md for guidance)
- **Contains**: Instructions, workflows, best practices, examples
- **Editable**: Yes - modify SKILL.md to update skill behavior

### skills-dist/ (Distribution)
- **Purpose**: Distributable packages for end users
- **Technology**: .skill files (zip archives)
- **Used by**: End users installing the skill
- **Contains**: Packaged versions of woosmap-skill/
- **Editable**: No - generated from woosmap-skill/

## Workflow

```
1. DEVELOP
   Edit: woosmap-skill/SKILL.md
   Test: Use Claude with the MCP server

2. PACKAGE
   Run: package_skill.py woosmap-skill skills-dist
   Output: skills-dist/woosmap.skill

3. DISTRIBUTE
   Share: skills-dist/woosmap.skill
   Install: Users extract to their skills folder
```

## Key Relationships

```
MCP Server ←→ Claude ←→ Skill Instructions
(woosmap/)              (woosmap-skill/)
    ↓                         ↓
    ↓                   Packaged into
    ↓                         ↓
Woosmap API           skills-dist/woosmap.skill
```

The MCP server provides the TOOLS (functions).
The skill provides the KNOWLEDGE (when/how to use them).


## Next Steps

1. Review the README files in each folder
2. Test the skill with Claude
3. Customize SKILL.md if needed
4. Package and distribute to users
