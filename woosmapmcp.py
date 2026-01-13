import sys
import logging
import debugpy
import os
import base64
import json
import io
from PIL import Image


from typing import Any, TypeAlias, Dict, List, Optional


import httpx
from mcp.server.fastmcp import FastMCP

Scalar: TypeAlias = str | int | float | bool | None
QueryParam: TypeAlias = tuple[str, Scalar]
QueryParams: TypeAlias = list[QueryParam]

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
if os.getenv("MCP_DEBUG") == "1":
    debugpy.listen(("127.0.0.1", 5678))

# Initialize FastMCP server
logger.debug("Starting Woosmap MCP server")
mcp = FastMCP("woosmapmcp")

# Constants
WOOSMAP_API_BASE = "https://api.woosmap.com"
USER_AGENT = "woosmapmcp-app/1.0"
API_KEY = os.getenv("WOOSMAP_API_KEY", "")
REF_ORIGIN = "https://www.woosmap.com"


async def make_woosmap_request(endpoint: str, params: dict[str, str]) -> dict[str, Any]:
    """Make a request to the Woosmap API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Origin": REF_ORIGIN}
    params["key"] = API_KEY
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{WOOSMAP_API_BASE}/{endpoint}",
                headers=headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}


async def image_url_to_base64(url: str, params: QueryParams) -> str:
    headers = {"User-Agent": USER_AGENT, "Origin": REF_ORIGIN}
    params.append(("key", API_KEY))
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            image_bytes = resp.content
            content_type = resp.headers.get("Content-Type", "").lower()
            if "image/webp" in content_type:
                logging.debug("Converting WebP image to PNG for Claude compatibility")
                return webp_bytes_to_png_base64(image_bytes)

            return base64.b64encode(resp.content).decode("utf-8")
        except Exception as e:
            logging.exception(f"Failed to fetch image from Woosmap Static API: {e}")
            return ""


def webp_bytes_to_png_base64(webp_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(webp_bytes)).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@mcp.tool()
async def get_places_nearby(
    latitude: float, longitude: float, radius: int, place_type: list[str]
) -> dict[str, Any] | None:
    """Get nearby places of a specific type using Woosmap localities/nearby API.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        radius: Search radius in meters. default is 1000 meters.
        place_type: list of type of place to search for (e.g., point_of_interest, transit.station, transit.station.airport, transit.station.rail, beach, business, business.car_repair, business.car_rental, business.cinema, business.conference_centre, business.exhibition_centre, business.theatre, business.nightclub, business.finance, business.finance.bank, business.fuel, business.parking, business.mall, business.food_and_drinks, business.food_and_drinks.bar, business.food_and_drinks.biergarten, business.food_and_drinks.cafe, business.food_and_drinks.fast_food, business.food_and_drinks.pub, business.food_and_drinks.restaurant, business.food_and_drinks.food_court, business.shop, business.shop.mall, business.shop.bakery, business.shop.butcher, business.shop.library, business.shop.grocery, business.shop.sports, business.shop.toys, business.shop.clothes, business.shop.furniture, business.shop.electronics, business.shop.doityourself, business.shop.craft, education, education.school, education.kindergarten, education.university, education.college, education.library, hospitality, hospitality.hotel, hospitality.hostel, hospitality.guest_house, hospitality.bed_and_breakfast, hospitality.motel, medical, medical.hospital, medical.pharmacy, medical.clinic, tourism, tourism.attraction, tourism.attraction.amusement_park, tourism.attraction.zoo, tourism.attraction.aquarium, tourism.monument, tourism.monument.castle, tourism.museum, government, park, park.national, place_of_worship, police, post_office, sports, sports.golf, sports.winter). default is point_of_interest.
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": str(radius),
        "types": "|".join(place_type),
    }
    try:
        data = await make_woosmap_request(
            "localities/nearby", params
        )  # fetching Woosmap Nearby Search API
        places = data.get("results", [])[:8]

        # # Build marker list
        # markers = []
        # for p in places:
        #     loc = p["geometry"]["location"]
        #     markers.append(
        #         {
        #             "lat": loc["lat"],
        #             "lng": loc["lng"],
        #             "url": "https://webapp.woosmap.com/img/geolocated_marker.png?retina=true",
        #         }
        #     )

        # params_img: QueryParams = [
        #     ("lat", f"{latitude}"),
        #     ("lng", f"{longitude}"),
        #     ("zoom", 14),
        #     ("width", 300),
        #     ("height", 300),
        #     ("retina", "yes"),
        # ]
        # for m in markers:
        #     params_img.append(("markers", json.dumps(m, separators=(",", ":"))))

        # places_image = await image_url_to_base64(
        #     f"{WOOSMAP_API_BASE}/maps/static", params_img
        # )

        # Build places list
        lines = []
        for i, p in enumerate(places, 1):
            lines.append(
                f"{i}. **{p.get('name', 'Unknown')}**\n"
                f"   {json.dumps(p, separators=(',', ':'))}\n"
                f"   Distance: {p.get('distance', 'N/A')} m"
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": "### Nearby \n\n" + "\n\n".join(lines),
                },
            ]
        }

        # return places
    except Exception as e:
        logging.exception("Woosmap nearby search failed")
        return {
            "error": str(e),
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "types": place_type,
        }


@mcp.tool()
async def get_place_details(
    public_id: str,
) -> Dict[str, Any]:
    """
    Get detailed information about a place using Woosmap Localities Details API.

    Args:
        public_id: Woosmap public_id of the place (returned by nearby/search APIs)
    """

    params = {
        "public_id": public_id,
    }

    try:
        data = await make_woosmap_request("localities/details", params)

        result = data.get("result", {})
        if not result:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No details found for public_id `{public_id}`.",
                    }
                ]
            }

        # Build readable summary
        lines = [
            f"**Name:** {result.get('name', 'Unknown')}",
            f"**Type:** {', '.join(result.get('types', []))}",
            f"**Address:** {result.get('formatted_address', 'N/A')}",
            f"**Country:** {result.get('country', 'N/A')}",
        ]

        if "geometry" in result:
            location = result["geometry"].get("location", {})
            lines.append(f"**Location:** {location.get('lat')}, {location.get('lng')}")

        if "contact" in result:
            contact = result["contact"]
            if contact.get("phone"):
                lines.append(f"**Phone:** {contact['phone']}")
            if contact.get("website"):
                lines.append(f"**Website:** {contact['website']}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "### Place Details\n\n" + "\n".join(lines) + "\n\n---\n\n"
                        "**Raw response:**\n"
                        f"{json.dumps(result, indent=2)}"
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Woosmap place details request failed")
        return {
            "error": str(e),
            "public_id": public_id,
        }


@mcp.tool()
async def autocomplete_then_details(
    input: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[int] = None,
    types: Optional[List[str]] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Autocomplete a place/address and automatically fetch details
    for the top prediction.

    Args:
        input: Text input (e.g. "Eiffel Tow").
        latitude: Optional latitude for location biasing.
        longitude: Optional longitude for location biasing.
        radius: Optional radius (meters).
        types: Optional list of place types.
        language: Optional response language.
    """

    # -----------------------------
    # Step 1: Autocomplete
    # -----------------------------
    autocomplete_params: Dict[str, Any] = {
        "input": input,
    }

    if latitude is not None and longitude is not None:
        autocomplete_params["location"] = f"{latitude},{longitude}"

    if radius is not None:
        autocomplete_params["radius"] = radius

    if types:
        autocomplete_params["types"] = "|".join(types)

    if language:
        autocomplete_params["language"] = language

    try:
        autocomplete_data = await make_woosmap_request(
            "localities/autocomplete",
            autocomplete_params,
        )

        predictions = autocomplete_data.get("predictions", [])
        if not predictions:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No autocomplete results for `{input}`.",
                    }
                ]
            }

        top_prediction = predictions[0]
        public_id = top_prediction.get("public_id")

        if not public_id:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Top autocomplete result has no public_id.",
                    }
                ]
            }

        # -----------------------------
        # Step 2: Details
        # -----------------------------
        details_data = await make_woosmap_request(
            "localities/details",
            {"public_id": public_id},
        )

        result = details_data.get("result", {})
        if not result:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No details found for public_id `{public_id}`.",
                    }
                ]
            }

        # -----------------------------
        # Build response
        # -----------------------------
        lines = [
            f"**Selected prediction:** {top_prediction.get('description', 'Unknown')}",
            f"**public_id:** `{public_id}`",
            "",
            "### Place Details",
            f"**Name:** {result.get('name', 'Unknown')}",
            f"**Address:** {result.get('formatted_address', 'N/A')}",
            f"**Types:** {', '.join(result.get('types', []))}",
        ]

        if "geometry" in result:
            loc = result["geometry"].get("location", {})
            lines.append(f"**Location:** {loc.get('lat')}, {loc.get('lng')}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "\n".join(lines) + "\n\n---\n\n"
                        "**Raw details:**\n"
                        f"{json.dumps(result, indent=2)}"
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Autocomplete → Details chain failed")
        return {
            "error": str(e),
            "input": input,
        }


@mcp.tool()
async def autocomplete_localities(
    input: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[int] = None,
    types: Optional[List[str]] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get place and address suggestions using Woosmap Localities Autocomplete API.

    Args:
        input: Text input from the user (e.g. "Eiffel To").
        latitude: Optional latitude for location biasing.
        longitude: Optional longitude for location biasing.
        radius: Optional radius (meters) for location biasing.
        types: Optional list of place types to filter results.
        language: Optional response language (ISO code, e.g. "en", "fr").
    """

    params: Dict[str, Any] = {
        "input": input,
    }

    if latitude is not None and longitude is not None:
        params["location"] = f"{latitude},{longitude}"

    if radius is not None:
        params["radius"] = radius

    if types:
        params["types"] = "|".join(types)

    if language:
        params["language"] = language

    try:
        data = await make_woosmap_request("localities/autocomplete", params)
        predictions = data.get("predictions", [])[:8]

        lines = []
        for i, p in enumerate(predictions, 1):
            lines.append(
                f"{i}. **{p.get('description', 'Unknown')}**\n"
                f"   Type: {', '.join(p.get('types', []))}\n"
                f"   public_id: `{p.get('public_id', 'N/A')}`\n"
                f"   Raw: {json.dumps(p, separators=(',', ':'))}"
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "### Autocomplete Suggestions\n\n" + "\n\n".join(lines)
                        if lines
                        else "No autocomplete suggestions found."
                    ),
                }
            ]
        }

    except Exception as e:
        logging.exception("Woosmap autocomplete request failed")
        return {
            "error": str(e),
            "input": input,
            "types": types,
        }


@mcp.tool()
async def geocode_locality(
    address: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[int] = None,
    language: Optional[str] = None,
    components: Optional[str] = None,
    bounds: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Geocode an address or place name using Woosmap Localities Geocode API.

    Args:
        address: Address or place name to geocode.
        latitude: Optional latitude for location biasing.
        longitude: Optional longitude for location biasing.
        radius: Optional radius (meters) for location biasing.
        language: Optional response language (ISO code, e.g. "en").
        components: Optional component filters (e.g. "country:IN").
        bounds: Optional bounding box bias
                Format: "sw_lat,sw_lng|ne_lat,ne_lng"
    """

    params: Dict[str, Any] = {
        "address": address,
    }

    if latitude is not None and longitude is not None:
        params["location"] = f"{latitude},{longitude}"

    if radius is not None:
        params["radius"] = radius

    if language:
        params["language"] = language

    if components:
        params["components"] = components

    if bounds:
        params["bounds"] = bounds

    try:
        data = await make_woosmap_request("localities/geocode", params)
        results = data.get("results", [])[:5]

        if not results:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No geocoding results found for `{address}`.",
                    }
                ]
            }

        lines = []
        for i, r in enumerate(results, 1):
            location = r.get("geometry", {}).get("location", {})
            lines.append(
                f"{i}. **{r.get('formatted_address', 'Unknown')}**\n"
                f"   Lat/Lng: {location.get('lat')}, {location.get('lng')}\n"
                f"   Types: {', '.join(r.get('types', []))}\n"
                f"   public_id: `{r.get('public_id', 'N/A')}`\n"
                f"   Raw: {json.dumps(r, separators=(',', ':'))}"
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": "### Geocode Results\n\n" + "\n\n".join(lines),
                }
            ]
        }

    except Exception as e:
        logging.exception("Woosmap geocode request failed")
        return {
            "error": str(e),
            "address": address,
            "components": components,
            "bounds": bounds,
        }


@mcp.tool()
async def reverse_geocode_locality(
    latitude: float,
    longitude: float,
    language: Optional[str] = None,
    components: Optional[str] = None,
    bounds: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reverse geocode coordinates to an address using Woosmap Localities Geocode API.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        language: Optional response language (ISO code, e.g. "en").
        components: Optional component filters (e.g. "country:IN").
        bounds: Optional bounding box bias
                Format: "sw_lat,sw_lng|ne_lat,ne_lng"
    """

    params: Dict[str, Any] = {
        "latlng": f"{latitude},{longitude}",
    }

    if language:
        params["language"] = language

    if components:
        params["components"] = components

    if bounds:
        params["bounds"] = bounds

    try:
        data = await make_woosmap_request("localities/geocode", params)
        results = data.get("results", [])[:5]

        if not results:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"No reverse-geocoding results for `{latitude},{longitude}`.",
                    }
                ]
            }

        lines = []
        for i, r in enumerate(results, 1):
            location = r.get("geometry", {}).get("location", {})
            lines.append(
                f"{i}. **{r.get('formatted_address', 'Unknown')}**\n"
                f"   Lat/Lng: {location.get('lat')}, {location.get('lng')}\n"
                f"   Types: {', '.join(r.get('types', []))}\n"
                f"   public_id: `{r.get('public_id', 'N/A')}`\n"
                f"   Raw: {json.dumps(r, separators=(',', ':'))}"
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": "### Reverse Geocode Results\n\n" + "\n\n".join(lines),
                }
            ]
        }

    except Exception as e:
        logging.exception("Woosmap reverse geocode request failed")
        return {
            "error": str(e),
            "latlng": f"{latitude},{longitude}",
            "components": components,
            "bounds": bounds,
        }


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
    mode: Optional[str] = None,
    units: Optional[str] = None,
    language: Optional[str] = None,
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
        language: Response language (ISO code).
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


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
