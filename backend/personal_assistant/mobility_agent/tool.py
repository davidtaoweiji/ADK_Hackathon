import requests
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MOBILITY_API_KEY")


def estimate_travel_time(start: str, destination: str, mode: str) -> str:
    """
    Estimates the travel time between two locations using the Google Maps Distance Matrix API.

    Args:
        start (str): The starting address or location name.
        destination (str): The destination address or location name.
        mode (str): Mode of transportation. Options include 'driving', 'walking', 'bicycling', or 'transit'.

    Returns:
        str: The estimated travel duration as a human-readable string (e.g., '25 mins'),
             or an error message if the request fails.
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start,
        "destinations": destination,
        "mode": mode,
        "departure_time": "now",
        "key": API_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and "rows" in data:
        duration = data["rows"][0]["elements"][0]["duration"]["text"]
        return duration
    else:
        return "Error: Unable to fetch travel time."


def geocode_address_coordinates(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200 and data["results"]:
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None


def geocode(address):
    """
    Geocodes a given address using the Google Maps Geocoding API.
    Args:
        address (str): The address or location name to geocode.
    Returns:
        dict: A dictionary containing the latitude ('lat'), longitude ('lng'),
              formatted address ('address'), and place ID ('place_id') if successful.
        or string: An error message if geocoding fails.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(base_url, params=params)
    data = response.json()
    if data["status"] != "OK":
        return "Error: Unable to fetch weather data."
    result = data["results"][0]
    location = result["geometry"]["location"]
    place_id = result["place_id"]
    formatted_address = result["formatted_address"]
    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "address": formatted_address,
        "place_id": place_id,
    }


def get_current_weather(address: str) -> dict:
    """
    Retrieves the current weather conditions for a given address.

    Args:
        address (str): The address or location name to get weather information for.

    Returns:
        dict: A dictionary containing current conditions if successful,
                or an error message if geocoding or weather data retrieval fails.
    """
    lat, lng = geocode_address_coordinates(address)
    if lat is None or lng is None:
        return {"error": "Unable to geocode address"}

    url = "https://weather.googleapis.com/v1/currentConditions:lookup"
    params = {"location.latitude": lat, "location.longitude": lng, "key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Unable to fetch weather data: {response.status_code} - {response.text}"
        }


def get_future_weather(address: str) -> dict:
    """
    Retrieves the future weather conditions for a given address.

    Args:
        address (str): The address or location name to get weather information for.

    Returns:
        dict: A dictionary ontaining the future weather details if successful,
                or an error message if geocoding or weather data retrieval fails.
    """
    lat, lng = geocode_address_coordinates(address)
    if lat is None or lng is None:
        return {"error": "Unable to geocode address"}
    url = "https://weather.googleapis.com/v1/forecast/hours:lookup"
    params = {
        "location.latitude": lat,
        "location.longitude": lng,
        "hours": 24,
        "key": API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch weather data"}


def get_uber_link(pickup_address: str, dropoff_address: str) -> str:
    """
    Generates a deep link for booking an Uber ride between two addresses.

    This function takes the pickup and dropoff addresses and constructs a URL-encoded Uber deep link that can be
    opened in a browser or mobile device to initiate the ride booking process with the specified locations.

    Args:
        pickup_address (str): The starting address for the Uber ride.
        dropoff_address (str): The destination address for the Uber ride.

    Returns:
        str: A URL (deep link) that opens the Uber app or website with the pickup and dropoff locations pre-filled.
    """
    pickup = geocode(pickup_address)
    dropoff = geocode(dropoff_address)

    # Build pickup and dropoff JSON objects
    pickup_data = {
        "addressLine1": pickup["address"],
        "latitude": pickup["lat"],
        "longitude": pickup["lng"],
        "id": pickup["place_id"],
        "source": "SEARCH",
    }

    dropoff_data = {
        "addressLine1": dropoff["address"],
        "latitude": dropoff["lat"],
        "longitude": dropoff["lng"],
        "id": dropoff["place_id"],
        "source": "SEARCH",
    }

    # URL encode the JSON strings
    pickup_encoded = urllib.parse.quote(json.dumps(pickup_data))
    dropoff_encoded = urllib.parse.quote(json.dumps(dropoff_data))

    # Construct the Uber deep link
    uber_link = (
        f"https://m.uber.com/go/product-selection?"
        f"pickup={pickup_encoded}&drop%5B0%5D={dropoff_encoded}"
    )

    return uber_link


def format_recommendations(recommendations):
    if not recommendations:
        return []
    formatted = []
    for place in recommendations:
        formatted.append(
            {
                "name": place.get("displayName", {}).get("text", "Name not available"),
                "address": place.get("formattedAddress", "Address not available"),
                "rating": place.get("rating", "Rating not available"),
                "opening_hours": place.get("currentOpeningHours", {}).get(
                    "weekdayDescriptions", "Opening hours not available"
                ),
                "price_range": {
                    "start_price": place.get("priceRange", {})
                    .get("startPrice", {})
                    .get("units", "Price not available"),
                    "end_price": place.get("priceRange", {})
                    .get("endPrice", {})
                    .get("units", "Price not available"),
                    "currency": place.get("priceRange", {})
                    .get("startPrice", {})
                    .get("currencyCode", "Currency not available"),
                },
            }
        )
    return formatted


def recommend_food_places(address: str, num_results: int, food_type: str) -> list:
    """
    Recommends food places near a given address using the Google Places API.

    This function geocodes the provided address to latitude and longitude, then searches for nearby food-related places
    (such as restaurants, cafes, bakeries, bars, or takeout) based on the specified food type. If no food type is provided,
    it searches for a default set of food-related place types. The results are formatted and returned as a list of recommendations.

    Args:
        address (str): The address or location name to search near.
        num_results (int): The maximum number of results to return for each food_type.
        food_type (str): The type of food place to search for ("restaurant", "cafe", "bakery", "bar", "meal_takeaway"). If None, this function will search all types.

    Returns:
        list: A list of dictionaries, each containing information about a recommended food place (name, address, rating, opening hours).
    """
    lat, lng = geocode_address_coordinates(address)
    food_types = (
        [food_type]
        if food_type
        else ["restaurant", "cafe", "bakery", "bar", "meal_takeaway"]
    )
    food_recommendations = []
    for place_type in food_types:
        food_recommendations.extend(nearby_search(lat, lng, place_type, num_results))
    return format_recommendations(food_recommendations)


def recommend_entertainment_places(
    address: str, num_results: int, entertainment_type: str
) -> list:
    """
    Recommends entertainment places near a given address using the Google Places API.

    This function geocodes the provided address to latitude and longitude, then searches for nearby entertainment-related places
    (such as movie theaters, amusement parks, night clubs, bowling alleys, or museums) based on the specified entertainment type.
    If no entertainment type is provided, it searches for a default set of entertainment-related place types.
    The results are formatted and returned as a list of recommendations.

    Args:
        address (str): The address or location name to search near.
        num_results (int): The maximum number of results return for each entertainment_type.
        entertainment_type (str): The type of entertainment place to search for ("movie_theater", "amusement_park", "night_club", "bowling_alley", "museum"). If None, this function will search all types.

    Returns:
        list: A list of dictionaries, each containing information about a recommended entertainment place (name, address, rating, opening hours).
    """
    lat, lng = geocode_address_coordinates(address)
    entertainment_types = (
        [entertainment_type]
        if entertainment_type
        else [
            "movie_theater",
            "amusement_park",
            "night_club",
            "bowling_alley",
            "museum",
        ]
    )
    entertainment_recommendations = []
    for place_type in entertainment_types:
        entertainment_recommendations.extend(
            nearby_search(lat, lng, place_type, num_results)
        )

    return format_recommendations(entertainment_recommendations)


def nearby_search(lat, lng, place_type, num_results):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.currentOpeningHours.weekdayDescriptions,places.priceRange",
    }
    body = {
        "includedTypes": [place_type],
        "maxResultCount": num_results,
        "locationRestriction": {
            "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 1500.0}
        },
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    return data.get("places", [])
