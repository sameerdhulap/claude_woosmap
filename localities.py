import json
import logging
from typing import Any, Dict, List, Optional

from core import mcp, make_woosmap_request

logger = logging.getLogger(__name__)


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
    latitude: float,
    longitude: float,
    components: list[str],
    radius: Optional[int] = None,
    types: Optional[List[str]] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Autocomplete a place/address and automatically fetch details
    for the top prediction.

    Args:
        input: Text input (e.g. "Eiffel Tow").
        latitude: latitude for location biasing.
        longitude: longitude for location biasing.
        components: country code in ISO_3166-1 format  (e.g. "IN","FR","US").
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

    if components:
        autocomplete_params["components"] = "|".join(f"country:{c}" for c in components)

    if language:
        autocomplete_params["language"] = language

    try:
        autocomplete_data = await make_woosmap_request(
            "localities/autocomplete",
            autocomplete_params,
        )

        predictions = autocomplete_data.get("localities", [])
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
    latitude: float,
    longitude: float,
    components: list[str],
    radius: Optional[int] = None,
    types: Optional[List[str]] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get place and address suggestions using Woosmap Localities Autocomplete API.

    Args:
        input: Text input from the user (e.g. "Eiffel To").
        latitude: latitude for location biasing.
        longitude: longitude for location biasing.
        components: country code in ISO_3166-1 format  (e.g. "IN","FR","US").
        radius: Optional radius (meters) for location biasing.
        types: Optional list of place types to filter results.
        language: Optional response language (ISO code, e.g. "en", "fr").
    """

    params: Dict[str, Any] = {
        "input": input,
    }

    if latitude is not None and longitude is not None:
        params["location"] = f"{latitude},{longitude}"

    if components:
        params["components"] = "|".join(f"country:{c}" for c in components)

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
