import sys
import logging
import debugpy
import os

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

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


async def make_woosmap_request(
    endpoint: str, params: dict[str, str]
) -> dict[str, Any] | None:
    """Make a request to the Woosmap API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Origin": "https://www.woosmap.com"}
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
            return None


@mcp.tool()
async def get_places_nearby(
    latitude: float, longitude: float, radius: int, place_type: str
) -> dict[str, Any] | None:
    """Get nearby places of a specific type using Woosmap localities/nearby API.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        radius: Search radius in meters. default is 1000 meters.
        place_type: Type of place to search for (e.g., point_of_interest, transit.station, transit.station.airport, transit.station.rail, beach, business, business.car_repair, business.car_rental, business.cinema, business.conference_centre, business.exhibition_centre, business.theatre, business.nightclub, business.finance, business.finance.bank, business.fuel, business.parking, business.mall, business.food_and_drinks, business.food_and_drinks.bar, business.food_and_drinks.biergarten, business.food_and_drinks.cafe, business.food_and_drinks.fast_food, business.food_and_drinks.pub, business.food_and_drinks.restaurant, business.food_and_drinks.food_court, business.shop, business.shop.mall, business.shop.bakery, business.shop.butcher, business.shop.library, business.shop.grocery, business.shop.sports, business.shop.toys, business.shop.clothes, business.shop.furniture, business.shop.electronics, business.shop.doityourself, business.shop.craft, education, education.school, education.kindergarten, education.university, education.college, education.library, hospitality, hospitality.hotel, hospitality.hostel, hospitality.guest_house, hospitality.bed_and_breakfast, hospitality.motel, medical, medical.hospital, medical.pharmacy, medical.clinic, tourism, tourism.attraction, tourism.attraction.amusement_park, tourism.attraction.zoo, tourism.attraction.aquarium, tourism.monument, tourism.monument.castle, tourism.museum, government, park, park.national, place_of_worship, police, post_office, sports, sports.golf, sports.winter). default is point_of_interest.
    """
    params = {
        "location": f"{latitude},{longitude}",
        "radius": str(radius),
        "types": place_type,
    }
    try:
        return await make_woosmap_request("localities/nearby", params)
    except Exception as e:
        logging.exception("Woosmap nearby search failed")
        return {
            "error": str(e),
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "types": place_type,
        }


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
