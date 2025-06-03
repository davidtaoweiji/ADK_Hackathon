import requests
import json
import urllib.parse

def geocode(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(base_url, params=params)
    data = response.json()
    if data["status"] != "OK":
        raise Exception(f"Geocoding failed: {data['status']}")
    result = data["results"][0]
    location = result["geometry"]["location"]
    return location["lat"], location["lng"]

def nearby_search(lat, lng, place_type, api_key, num_results):
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
        raise Exception(f"Nearby search failed: {data['status']}")
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
