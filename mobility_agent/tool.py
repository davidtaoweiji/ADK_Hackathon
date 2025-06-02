import requests
import urllib.parse
import json

api_key='AIzaSyBVMS-qnZebtj6QzeAy6HDbwCDyFIzD0XA'
def estimate_travel_time(start, destination, mode):
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
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': start,
        'destinations': destination,
        'mode': mode,
        'departure_time': 'now',
        'key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200 and 'rows' in data:
        duration = data['rows'][0]['elements'][0]['duration']['text']
        return duration
    else:
        return "Error: Unable to fetch travel time."
    
def geocode_address_coordinates(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200 and data['results']:
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
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
    params = {"address": address, "key": api_key}
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
        "place_id": place_id
    }

def get_weather(address):
    """
    Retrieves the current weather conditions and forecast for a given address.

    This function first geocodes the provided address to obtain its latitude and longitude,
    then queries the Google Weather API to fetch the current weather and forecast data.

    Args:
        address (str): The address or location name to get weather information for.

    Returns:
        tuple: (current_conditions, forecast) if successful,
        or str: An error message if geocoding or weather data retrieval fails.
    """
    lat, lng = geocode_address_coordinates(address, api_key)
    if lat is None or lng is None:
        return "Error: Unable to geocode address."
    
    url = 'https://weather.googleapis.com/v1/weather:lookup'
    params = {
        'location.latitude': lat,
        'location.longitude': lng,
        'fields': 'currentConditions,forecast',
        'key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200 and 'currentConditions' in data:
        current_conditions = data['currentConditions']
        forecast = data['forecast']
        return current_conditions, forecast
    else:
        return "Error: Unable to fetch weather data."

def get_uber_link(pickup_address, dropoff_address):
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
        "source": "SEARCH"
    }

    dropoff_data = {
        "addressLine1": dropoff["address"],
        "latitude": dropoff["lat"],
        "longitude": dropoff["lng"],
        "id": dropoff["place_id"],
        "source": "SEARCH"
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

def nearby_search(lat, lng, place_type, num_results):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 1500,
        "type": place_type,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data["status"] != "OK":
        return ["error: Unable to fetch nearby places."]
    return data["results"][:num_results]

def format_recommendations(recommendations):
    formatted = []
    for place in recommendations:
        formatted.append({
            "name": place["name"],
            "address": place.get("vicinity", "Address not available"),
            "rating": place.get("rating", "Rating not available"),
            "opening_hours": place.get("opening_hours", {}).get("open_now", "Opening hours not available")
        })
    return formatted

def recommend_food_places(address, num_results,food_type):
    """
    Recommends food places near a given address using the Google Places API.

    This function geocodes the provided address to latitude and longitude, then searches for nearby food-related places
    (such as restaurants, cafes, bakeries, bars, or takeout) based on the specified food type. If no food type is provided,
    it searches for a default set of food-related place types. The results are formatted and returned as a list of recommendations.

    Args:
        address (str): The address or location name to search near.
        num_results (int): The maximum number of results to return.
        food_type (str): The type of food place to search for (e.g., 'restaurant', 'cafe'). If None, searches multiple types.

    Returns:
        list: A list of dictionaries, each containing information about a recommended food place (name, address, rating, opening hours).
    """
    lat, lng = geocode_address_coordinates(address)
    food_types = [food_type] if food_type else ["restaurant", "cafe", "bakery", "bar", "meal_takeaway"]
    food_recommendations = []
    for place_type in food_types:
        food_recommendations.extend(nearby_search(lat, lng, place_type, num_results))
    return format_recommendations(food_recommendations)


def recommend_entertainment_places(address, num_results, entertainment_type):
    """
    Recommends entertainment places near a given address using the Google Places API.

    This function geocodes the provided address to latitude and longitude, then searches for nearby entertainment-related places
    (such as movie theaters, amusement parks, night clubs, bowling alleys, or museums) based on the specified entertainment type.
    If no entertainment type is provided, it searches for a default set of entertainment-related place types.
    The results are formatted and returned as a list of recommendations.

    Args:
        address (str): The address or location name to search near.
        num_results (int): The maximum number of results to return.
        entertainment_type (str): The type of entertainment place to search for (e.g., 'movie_theater', 'museum'). If None, searches multiple types.

    Returns:
        list: A list of dictionaries, each containing information about a recommended entertainment place (name, address, rating, opening hours).
    """
    lat, lng = geocode_address_coordinates(address)
    entertainment_types = [entertainment_type] if entertainment_type else ["movie_theater", "amusement_park", "night_club", "bowling_alley", "museum"]
    entertainment_recommendations = []
    for place_type in entertainment_types:
        entertainment_recommendations.extend(nearby_search(lat, lng, place_type, num_results))
    return format_recommendations(entertainment_recommendations)


if __name__ == "__main__":
    # start_location = "Space Karaoke Bar & Cafe"
    # destination_location = "CBRE Richardson"
    # travel_mode = "driving"  # Options: 'driving', 'walking
    # distance = estimate_travel_time(start_location, destination_location, travel_mode)
    # print(f"Estimated travel time from {start_location} to {destination_location} by {travel_mode}: {distance}")
    # print(f"Weather at: {get_uber_link("Space Karaoke Bar & Cafe","CBRE Richardson")}")
    # Example Uber deep link generation
    print(recommend_food_places("Space Karaoke Bar & Cafe", 5, "restaurant"))