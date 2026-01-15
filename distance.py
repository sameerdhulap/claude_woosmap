import json
from typing import Any, Dict, List, Optional
import logging

from core import mcp, make_woosmap_request

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_route_distance(
    origin: str,
    destination: str,
    waypoints: Optional[List[str]] = None,
    mode: Optional[str] = None,
    method: Optional[str] = None,
    language: Optional[str] = None,
    units: Optional[str] = None,
    alternatives: Optional[bool] = None,
    avoid: Optional[str] = None,
    departure_time: Optional[str] = None,
    arrival_time: Optional[str] = None,
    details: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a route and return detailed distance, duration, and path using Woosmap Distance Route API.

    Args:
        origin: "lat,lng" of the start point.
        destination: "lat,lng" of the end point.
        waypoints: Optional list of "lat,lng" points.
        mode: Travel mode ("driving","walking","cycling").
        method: Route computation method ("time","distance").
        language: Output language (ISO code).
        units: "metric" or "imperial".
        alternatives: Include alternative routes.
        avoid: Routing avoids ("tolls","highways", etc.).
        departure_time: Timestamp or "now" for traffic.
        arrival_time: Timestamp for arrival time calculation.
        details: "full" for full roadbook instructions.
    """

    params: Dict[str, Any] = {
        "origin": origin,
        "destination": destination,
    }

    if waypoints:
        # Pipe-separated list according to spec
        params["waypoints"] = "|".join(waypoints)

    if mode:
        params["mode"] = mode
    if method:
        params["method"] = method
    if language:
        params["language"] = language
    if units:
        params["units"] = units
    if alternatives is not None:
        params["alternatives"] = str(alternatives).lower()
    if avoid:
        params["avoid"] = avoid
    if departure_time:
        params["departure_time"] = departure_time
    if arrival_time:
        params["arrival_time"] = arrival_time
    if details:
        params["details"] = details

    try:
        data = await make_woosmap_request("distance/route/json", params)

        status = data.get("status", "UNKNOWN")
        routes = data.get("routes", [])

        if not routes:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No route found for {origin} → {destination}. Status: {status}",
                    }
                ]
            }

        # Summarize the first route
        r = routes[0]
        summary_lines = [
            f"**Status:** {status}",
            f"**Origin:** {origin}",
            f"**Destination:** {destination}",
        ]

        if "bounds" in r:
            bounds = r["bounds"]
            summary_lines.append(
                f"**Bounds:** NE({bounds.get('northeast')}), "
                f"SW({bounds.get('southwest')})"
            )

        if "overview_polyline" in r:
            summary_lines.append(
                f"**Polyline:** {r['overview_polyline'].get('points')}"
            )

        # legs: total distance/duration
        legs = r.get("legs", [])
        if legs:
            total_distance = sum(
                leg.get("distance", {}).get("value", 0) for leg in legs
            )
            total_duration = sum(
                leg.get("duration", {}).get("value", 0) for leg in legs
            )
            summary_lines.append(f"**Total distance:** {total_distance} m")
            summary_lines.append(f"**Total duration:** {total_duration} sec")

        return {
            "content": [
                {
                    "type": "text",
                    "text": "### Route Summary\n\n"
                    + "\n".join(summary_lines)
                    + "\n\n**Full JSON:**\n"
                    + json.dumps(data, indent=2),
                }
            ]
        }

    except Exception as e:
        logging.exception("Route distance request failed")
        return {
            "error": str(e),
            "origin": origin,
            "destination": destination,
        }


@mcp.tool()
async def get_distance_matrix(
    origins: List[str],
    destinations: List[str],
    language: str,
    mode: Optional[str] = None,
    units: Optional[str] = None,
    departure_time: Optional[str] = None,
    avoid: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a distance and duration matrix using Woosmap Distance Matrix API.

    Args:
        origins: List of "lat,lng" origin points.
        destinations: List of "lat,lng" destination points.
        mode: Travel mode ("driving", "walking", "cycling").
        units: "metric" or "imperial".
        language: Request language (ISO code).
        departure_time: "now" or timestamp for traffic-aware durations.
        avoid: Routing constraints (e.g. "tolls", "highways").
    """

    params: Dict[str, Any] = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
    }

    if mode:
        params["mode"] = mode
    if units:
        params["units"] = units
    if language:
        params["language"] = language
    if departure_time:
        params["departure_time"] = departure_time
    if avoid:
        params["avoid"] = avoid

    try:
        data = await make_woosmap_request(
            "distance/distancematrix/json",
            params,
        )

        status = data.get("status", "UNKNOWN")
        rows = data.get("rows", [])

        if not rows:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No distance matrix results. Status: {status}",
                    }
                ]
            }

        # Build readable matrix summary
        lines = [f"**Status:** {status}", ""]

        for i, row in enumerate(rows):
            elements = row.get("elements", [])
            lines.append(f"### Origin {i + 1}")
            for j, el in enumerate(elements):
                distance = el.get("distance", {}).get("value")
                duration = el.get("duration", {}).get("value")
                el_status = el.get("status", "UNKNOWN")

                lines.append(
                    f"- To destination {j + 1}: "
                    f"{distance} m, {duration} sec (status: {el_status})"
                )
            lines.append("")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "### Distance Matrix\n\n" + "\n".join(lines) + "\n\n---\n\n"
                        "**Raw response:**\n" + json.dumps(data, indent=2)
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Distance matrix request failed")
        return {
            "error": str(e),
            "origins": origins,
            "destinations": destinations,
        }


@mcp.tool()
async def get_route_tolls(
    origin: str,
    destination: str,
    waypoints: Optional[List[str]] = None,
    mode: Optional[str] = None,
    currency: Optional[str] = None,
    units: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    vehicle_emission_type: Optional[str] = None,
    axle_count: Optional[int] = None,
    departure_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate toll costs for a route using Woosmap Distance Tolls API.

    Args:
        origin: "lat,lng" of the start point.
        destination: "lat,lng" of the end point.
        waypoints: Optional list of "lat,lng" waypoints.
        mode: Travel mode ("driving").
        currency: ISO currency code (e.g. "EUR", "USD", "INR").
        units: "metric" or "imperial".
        vehicle_type: Vehicle type (e.g. "car", "truck").
        vehicle_emission_type: Emission standard (e.g. "euro6").
        axle_count: Number of axles (required for trucks).
        departure_time: "now" or timestamp.
    """

    params: Dict[str, Any] = {
        "origin": origin,
        "destination": destination,
    }

    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    if mode:
        params["mode"] = mode
    if currency:
        params["currency"] = currency
    if units:
        params["units"] = units
    if vehicle_type:
        params["vehicle_type"] = vehicle_type
    if vehicle_emission_type:
        params["vehicle_emission_type"] = vehicle_emission_type
    if axle_count is not None:
        params["axle_count"] = axle_count
    if departure_time:
        params["departure_time"] = departure_time

    try:
        data = await make_woosmap_request(
            "distance/tolls/json",
            params,
        )

        status = data.get("status", "UNKNOWN")
        routes = data.get("routes", [])

        if not routes:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No toll route found. Status: {status}",
                    }
                ]
            }

        # Use first route
        route = routes[0]
        tolls = route.get("tolls", [])

        lines = [
            f"**Status:** {status}",
            f"**Origin:** {origin}",
            f"**Destination:** {destination}",
            "",
            "### Toll Summary",
        ]

        total_cost = 0.0
        currency_code = currency or "N/A"

        for t in tolls:
            cost = t.get("price", {}).get("value", 0)
            total_cost += cost
            lines.append(
                f"- {t.get('name', 'Toll')} — {cost} {t.get('price', {}).get('currency', currency_code)}"
            )

        lines.append("")
        lines.append(f"**Total toll cost:** {total_cost} {currency_code}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "### Route Tolls\n\n" + "\n".join(lines) + "\n\n---\n\n"
                        "**Raw response:**\n" + json.dumps(data, indent=2)
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Tolls request failed")
        return {
            "error": str(e),
            "origin": origin,
            "destination": destination,
        }
