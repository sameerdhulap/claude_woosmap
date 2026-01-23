# Woosmap Skill Installation Guide

This guide explains how to install and configure the Woosmap skill for Claude.

## What This Skill Provides

The Woosmap skill enables Claude to:
- Search for places and addresses
- Find nearby locations (restaurants, coffee shops, etc.)
- Get directions and routes
- Geocode addresses to coordinates
- Calculate distances and travel times
- Get toll costs for routes
- Plan public transit routes

## Prerequisites

- Claude Desktop installed
- Python 3.10 or higher
- A Woosmap API key (free tier available)

## Installation Steps

### 1. Install the Skill

1. Download `woosmap-skill.skill`
2. In Claude Desktop, go to Settings → Skills
3. Click "Install Skill" and select the downloaded `.skill` file

### 2. Get a Woosmap API Key

1. Visit [Woosmap Console](https://console.woosmap.com/)
2. Sign up for a free account
3. Create a new project
4. Generate an API key from the project dashboard
5. Copy your API key

### 3. Configure the MCP Server

The Woosmap skill requires an MCP server to communicate with the Woosmap API. Here's how to set it up:

#### Option A: Using Python (Recommended)

1. **Find the skill location:**
   - macOS: `~/Library/Application Support/Claude/skills/woosmap/`
   - Windows: `%APPDATA%\Claude\skills\woosmap\`

2. **Install dependencies:**
   ```bash
   cd ~/Library/Application\ Support/Claude/skills/woosmap/scripts/
   pip install -e . --break-system-packages
   ```

3. **Configure Claude Desktop:**
   
   Edit your Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   
   Add this configuration (replace `<YOUR_API_KEY>` with your actual API key):
   
   ```json
   {
     "mcpServers": {
       "woosmap": {
         "command": "python",
         "args": ["-m", "main"],
         "cwd": "/Users/<YOUR_USERNAME>/Library/Application Support/Claude/skills/woosmap/scripts/",
         "env": {
           "WOOSMAP_API_KEY": "<YOUR_API_KEY>",
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

   **Note:** Update the `cwd` path to match your system:
   - macOS: `/Users/<YOUR_USERNAME>/Library/Application Support/Claude/skills/woosmap/scripts/`
   - Windows: `C:\Users\<YOUR_USERNAME>\AppData\Roaming\Claude\skills\woosmap\scripts\`

#### Option B: Using uv (Alternative)

If you have `uv` installed:

```bash
cd ~/Library/Application\ Support/Claude/skills/woosmap/scripts/
uv sync
```

Then in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "woosmap": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/<YOUR_USERNAME>/Library/Application Support/Claude/skills/woosmap/scripts/",
        "run",
        "main.py"
      ],
      "env": {
        "WOOSMAP_API_KEY": "<YOUR_API_KEY>",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

## Verification

Test that the skill is working by asking Claude:

- "Find coffee shops near me"
- "What's the distance from Paris to London?"
- "Get directions from Times Square to Central Park"
- "Find the nearest gas station"

If Claude can answer these questions using real location data, your skill is properly configured!

## Troubleshooting

### Skill doesn't work / Tools not available

1. **Check configuration file syntax:**
   - Make sure the JSON is valid (use a JSON validator)
   - Verify the `cwd` path exists and points to the correct location
   - Ensure there are no trailing commas

2. **Check API key:**
   - Verify your API key is correct
   - Check that the API key has the necessary permissions
   - Ensure you haven't exceeded your API quota

3. **Check logs:**
   - macOS: `tail -f ~/Library/Logs/Claude/mcp.log`
   - Windows: Check Event Viewer or application logs

4. **Verify MCP server runs:**
   ```bash
   cd ~/Library/Application\ Support/Claude/skills/woosmap/scripts/
   python -m main
   ```
   The server should start without errors. Press Ctrl+C to stop.

### No results returned

- Verify your WOOSMAP_API_KEY is set correctly
- Check API quotas and permissions in the Woosmap Console
- Try simpler queries first to verify basic functionality

### Import errors

Make sure dependencies are installed:
```bash
pip install httpx mcp debugpy pillow --break-system-packages
```

## Environment Variables

The following environment variable is **required**:

- **`WOOSMAP_API_KEY`**: Your Woosmap API key

Optional environment variables:

- **`PYTHONUNBUFFERED`**: Set to "1" for immediate log flushing
- **`MCP_DEBUG`**: Set to "1" to enable debug mode

## Support

For issues with:
- **The skill itself**: Check the troubleshooting section above
- **Woosmap API**: Visit [Woosmap Documentation](https://developers.woosmap.com/)
- **Claude Desktop**: Contact Anthropic support

## API Usage and Costs

The Woosmap API offers a free tier with usage limits. Monitor your usage in the [Woosmap Console](https://console.woosmap.com/) to avoid unexpected charges.
