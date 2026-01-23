---
name: woosmap
description: Geolocation and mapping services using the Woosmap API. Use this skill when users need to (1) search for places or addresses, (2) find nearby locations (e.g., "nearest coffee shop"), (3) get directions or routes between locations, (4) geocode addresses to coordinates, (5) reverse geocode coordinates to addresses, (6) calculate distances or travel times, (7) get toll costs for routes, or (8) plan public transit routes.
---

# Woosmap Geolocation & Mapping Skill

This skill provides guidance for using Woosmap API tools to handle location-based queries, address lookups, routing, and navigation tasks.

## Setup Requirements

This skill requires the Woosmap MCP server to be installed and configured. The MCP server is included in this skill's `scripts/` directory.

### For Claude Desktop (Local Use)

#### Installation Steps

1. **Install dependencies:**
   ```bash
   cd <skill-location>/scripts/
   pip install -e . --break-system-packages
   ```
   Or use uv:
   ```bash
   uv sync
   ```

2. **Get a Woosmap API key:**
   - Sign up at [Woosmap Console](https://console.woosmap.com/)
   - Create a project and generate an API key

3. **Configure Claude Desktop:**
   
   Edit your Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   
   Add the Woosmap MCP server:
   ```json
   {
     "mcpServers": {
       "woosmap": {
         "command": "python",
         "args": ["-m", "main"],
         "cwd": "<path-to-skill>/scripts/",
         "env": {
           "WOOSMAP_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** for changes to take effect

### For Web Claude (claude.ai)

Web Claude requires the MCP server to be hosted remotely. Two options:

#### Option 1: Deploy to Railway.app (Easiest)

1. Extract the `scripts/` folder from the skill
2. Deploy to [Railway.app](https://railway.app)
3. Set `WOOSMAP_API_KEY` environment variable
4. Connect to web Claude using the Railway URL

**See included deployment guides for detailed instructions.**

#### Option 2: Use Claude Desktop

For personal use, Claude Desktop is simpler as it runs the MCP server locally without needing to deploy to a hosting service.

### Verification

After restarting, you can verify the skill is working by asking:
- "Find coffee shops near me"
- "What's the distance from Paris to London?"

## Core Capabilities

### 1. Place Search & Autocomplete
- **autocomplete_localities**: Get place/address suggestions as user types
- **autocomplete_then_details**: Autocomplete and fetch details for top prediction in one step
- **get_place_details**: Get detailed information about a specific place using its public_id

### 2. Geocoding
- **geocode_locality**: Convert address/place name to geographic coordinates
- **reverse_geocode_locality**: Convert coordinates to human-readable address

### 3. Routing & Navigation
- **get_route_distance**: Compute detailed route with distance, duration, and turn-by-turn path
- **get_distance_matrix**: Calculate distances/durations between multiple origins and destinations
- **get_route_tolls**: Calculate toll costs for a route (useful for trip planning)
- **get_transit_route**: Compute public transport routes with schedules

## Common Workflows

### Finding Nearby Places
When user asks "Find nearest coffee shop" or "What restaurants are near me":

1. If you don't have user's location, ask for it or use location from context
2. Use `autocomplete_localities` with:
   - `input`: search term (e.g., "coffee shop")
   - `latitude` and `longitude`: user's location for biasing results
   - `components`: country code if known (e.g., ["US"])
   - `language`: user's preferred language
3. If details are needed, use `get_place_details` with the `public_id` from results

**Alternative**: Use `autocomplete_then_details` to get top result with details in one call

### Getting Directions
When user asks "How do I get from A to B" or "Directions to the airport":

1. If addresses provided, geocode them first using `geocode_locality`
2. Use `get_route_distance` with:
   - `origin`: "lat,lng" format
   - `destination`: "lat,lng" format
   - `mode`: "driving", "walking", or "cycling"
   - `departure_time`: "now" for traffic-aware routing
   - `details`: "full" for turn-by-turn instructions
   - `language`: for localized instructions
3. For public transit, use `get_transit_route` instead
4. For toll information, call `get_route_tolls` with same origin/destination

### Address Lookup
When user provides an address to find:

1. Use `geocode_locality` with:
   - `address`: the full address string
   - `language`: user's language
   - `components`: country filter if helpful
2. Optionally use `get_place_details` for comprehensive information

### Reverse Address Lookup
When user provides coordinates or asks "Where is 40.7128,-74.0060":

1. Use `reverse_geocode_locality` with:
   - `latitude` and `longitude`: the coordinates
   - `language`: for localized address format

## Best Practices

### Language & Location Parameters
- **Always specify `language`**: Use ISO 639-2 Alpha-2 codes ("en", "fr", "es", "de", etc.)
- **Use `components` for filtering**: Country codes in ISO 3166-1 format (["US"], ["FR"], ["IN"])
- **Provide location biasing**: Include `latitude` and `longitude` when available to get relevant nearby results
- **Set `radius`**: Optional, in meters, for fine-tuning proximity search

### Routing Parameters
- **Travel mode**: Choose "driving", "walking", or "cycling" based on user needs
- **Traffic awareness**: Use `departure_time: "now"` for real-time traffic consideration
- **Units**: Set to "metric" or "imperial" based on user's region/preference
- **Full details**: Use `details: "full"` when user needs turn-by-turn navigation
- **Waypoints**: Include intermediate stops as list of "lat,lng" strings
- **Route alternatives**: Set `alternatives: true` to get multiple route options
- **Avoid preferences**: Use `avoid` parameter ("tolls", "highways", etc.)

### Efficient Tool Selection
- Use `autocomplete_then_details` when you need place info immediately after search
- Use `get_distance_matrix` for comparing multiple routes at once
- Use `get_route_distance` when full turn-by-turn directions are required
- Use health_check to verify API connectivity before complex operations

### Transit Routing
- Specify `transit_modes`: Filter by ["bus", "subway", "train", "tram", "rail"]
- Use `departure_time` or `arrival_time` for schedule-based routing
- Results include step-by-step transit instructions with stops and schedules

## Parameter Formats

### Coordinates
Always use "lat,lng" string format: `"48.8584,2.2945"`

### Time Parameters
- Current time: `"now"`
- Specific time: Unix timestamp (integer) or ISO 8601 string

### Travel Modes
- Driving: `"driving"`
- Walking: `"walking"`
- Cycling: `"cycling"`
- Transit: Use `get_transit_route` with mode specification

### Distance Units
- Metric (km, m): `"metric"`
- Imperial (mi, ft): `"imperial"`

### Country Codes
- Use ISO 3166-1 Alpha-2: ["US"], ["GB"], ["FR"], ["IN"], etc.
- Can provide multiple: ["US", "CA"] for US and Canada

## Error Handling & Troubleshooting

### Geocoding Failures
- Try reformatting the address (add/remove components)
- Use broader search terms
- Check country code filter isn't too restrictive
- Verify address spelling

### Routing Errors
- Confirm coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)
- Verify travel mode is appropriate for the route
- Check that origin and destination are accessible by chosen mode
- For transit, ensure route is within service area

### API Response Issues
- Use `health_check` to verify API connectivity
- Check that language codes are valid ISO 639-2
- Verify country codes are ISO 3166-1 format
- Ensure required parameters are provided

## Examples

### Find Coffee Shop
```
User: "Find the nearest Starbucks"
1. autocomplete_localities(
     input="Starbucks",
     latitude=37.7749,
     longitude=-122.4194,
     components=["US"],
     language="en"
   )
2. get_place_details(public_id=<result_id>, language="en")
```

### Get Driving Directions
```
User: "Directions from Times Square to Central Park"
1. geocode_locality(address="Times Square, New York", language="en")
2. geocode_locality(address="Central Park, New York", language="en")
3. get_route_distance(
     origin="40.7580,-73.9855",
     destination="40.7829,-73.9654",
     mode="driving",
     departure_time="now",
     details="full",
     language="en",
     units="imperial"
   )
```

### Calculate Toll Costs
```
User: "How much are tolls from Boston to NYC?"
1. get_route_tolls(
     origin="42.3601,-71.0589",
     destination="40.7128,-74.0060",
     mode="driving",
     currency="USD",
     vehicle_type="car",
     departure_time="now"
   )
```
