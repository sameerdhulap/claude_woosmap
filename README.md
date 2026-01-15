## Woosmap MCP for Claude Desktop

This project provides a Model Context Protocol (MCP) server that integrates the Woosmap Nearby / Localities API with Claude Desktop, enabling Claude to find nearby places such as restaurants, businesses, and points of interest.

---

### Prerequisites
	
- Claude Desktop (macOS)
- Python 3.9+
- uv package manager
- A valid Woosmap API key

---

#### Installation

1. Install uv (if not already installed)
    
    ``` bash
    pip install uv
    or
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

_Or follow the official installation guide for your platform._

---

2. Clone or place the MCP code locally

    Make sure your MCP script (e.g. main.py) and dependencies are available in a local directory.

    ##### Example:
    ``` text
        woosmap-mcp/
        ├── main.py
        ├── pyproject.toml
        └── README.md
    ```

---
3. Download dependencies and verify the MCP runs correctly:
    ```sh
    uv sync
    uv run main.py
    ```

---

#### Configure Claude Desktop

1. Edit claude_desktop_config.json

Update your Claude Desktop configuration to register the Woosmap MCP.

```json
{
  "mcpServers": {
	  "WoosmapMcp": {
	    "command": "/Users/saturn/.local/bin/uv",
	    "args": [
	      "--directory",
	      "<<Location of code>>",
	      "run",
	      "main.py"
	    ],
	    "env": {
	      "PYTHONUNBUFFERED": "1",
	      "MCP_DEBUG": "1",
	      "WOOSMAP_API_KEY": "<<Your Woosmap Key>>"
	    }
	  }
	}
}
```

📍 Config file location (macOS):
```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

2. Restart Claude Desktop

Claude Desktop must be restarted for the MCP configuration to take effect.
---

### Usage

Once Claude Desktop is running:
1.	Open a new chat in Claude
2.	Ask a natural language query, for example:
    
    ```text
    Find a restaurant near Seattle
    ```

Claude will automatically invoke the Woosmap MCP and return nearby restaurants using the Woosmap Nearby API.

---

### Environment Variables
|Variable| Description|
|---|---|
|WOOSMAP_API_KEY|Your Woosmap API key|
|MCP_DEBUG|Enables MCP debug logging|
|PYTHONUNBUFFERED|Ensures logs are flushed immediately|

### Debugging & Logs

#### Claude MCP logs
```bash
tail -f ~/Library/Logs/Claude/mcp.log
```

#### Standalone test (recommended)

Before using Claude, verify the MCP runs correctly:
```sh
uv sync
uv run main.py
```

If this fails, Claude will not be able to load the MCP.

⸻

### Troubleshooting
- Tool not available in Claude
- Check claude_desktop_config.json syntax
- Ensure the MCP name matches exactly (WoosmapMcp)
- Restart Claude Desktop
- No results returned
- Verify WOOSMAP_API_KEY is valid
- Check API quotas and permissions
- Claude hangs
- Ensure no print() statements are used
- Logs must go to stderr, not stdout

---

### License

MIT

---

### Contributing

Contributions, bug reports, and feature requests are welcome.
Please open an issue or submit a pull request.
