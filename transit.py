import json
from typing import Any, Dict, List, Optional
import logging
from core import mcp, make_woosmap_request

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_transit_route(
    origin: str,
    destination: str,
    departure_time: Optional[str] = None,
    arrival_time: Optional[str] = None,
    language: Optional[str] = None,
    units: Optional[str] = None,
    transit_modes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compute a public transport route using Woosmap Transit Route API.

    Args:
        origin: "lat,lng" of the start point.
        destination: "lat,lng" of the end point.
        departure_time: "now" or timestamp (ISO or Unix).
        arrival_time: Timestamp for arrival-based routing.
        language: Response language (ISO code).
        units: "metric" or "imperial".
        transit_modes: Allowed transit modes
            (e.g. ["bus","subway","train","tram","rail"]).
    """

    params: Dict[str, Any] = {
        "origin": origin,
        "destination": destination,
    }

    if departure_time:
        params["departure_time"] = departure_time

    if arrival_time:
        params["arrival_time"] = arrival_time

    if language:
        params["language"] = language

    if units:
        params["units"] = units

    if transit_modes:
        params["transit_modes"] = "|".join(transit_modes)

    try:
        data = await make_woosmap_request(
            "transit/route",
            params,
        )

        status = data.get("status", "UNKNOWN")
        routes = data.get("routes", [])

        if not routes:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No transit route found. Status: {status}",
                    }
                ]
            }

        # Use first route
        route = routes[0]
        legs = route.get("legs", [])

        lines = [
            f"**Status:** {status}",
            f"**Origin:** {origin}",
            f"**Destination:** {destination}",
            "",
            "### Transit Itinerary",
        ]

        total_duration = 0
        total_distance = 0

        for leg in legs:
            leg_distance = leg.get("distance", {}).get("value", 0)
            leg_duration = leg.get("duration", {}).get("value", 0)

            total_distance += leg_distance
            total_duration += leg_duration

            steps = leg.get("steps", [])
            for step in steps:
                travel_mode = step.get("travel_mode", "UNKNOWN")
                instruction = step.get("html_instructions", "")
                lines.append(f"- **{travel_mode}**: {instruction}")

        lines.append("")
        lines.append(f"**Total distance:** {total_distance} m")
        lines.append(f"**Total duration:** {total_duration} sec")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "### Transit Route Summary\n\n"
                        + "\n".join(lines)
                        + "\n\n---\n\n"
                        "**Raw response:**\n" + json.dumps(data, indent=2)
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Transit route request failed")
        return {
            "error": str(e),
            "origin": origin,
            "destination": destination,
        }
