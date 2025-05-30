import requests
import urllib.parse
    
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
    
def geocode_address(address, api_key='AIzaSyCP6Ki0NBPhc2hR8OCUTnWTHTZ5niwTJt0'):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    if response.status_code == 200 and data['results']:
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None
    
def get_weather(lat,lng):
    # lat, lng = geocode_address(address, api_key)
    # if lat is None or lng is None:
    #     return "Error: Unable to geocode address."
    
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

import requests

def get_guest_trip_estimate(oauth_token, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    url = "https://sandbox-api.uber.com/v1/guests/trips/estimates"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json"
    }
    data = {
        "pickup": {
            "latitude": pickup_lat,
            "longitude": pickup_lng
        },
        "dropoff": {
            "latitude": dropoff_lat,
            "longitude": dropoff_lng
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    # start_location = "Space Karaoke Bar & Cafe"
    # destination_location = "CBRE Richardson"
    # travel_mode = "driving"  # Options: 'driving', 'walking
    # distance = estimate_travel_time(start_location, destination_location, travel_mode)
    # print(f"Estimated travel time from {start_location} to {destination_location} by {travel_mode}: {distance}")
    # print(f"Weather at: {get_weather("CBRE Richardson")}")
    token = "IA.VUNmGAAAAAAAEgASAAAABwAIAAwAAAAAAAAAEgAAAAAAAAGsAAAAFAAAAAAADgAQAAQAAAAIAAwAAAAOAAAAgAAAABwAAAAEAAAAEAAAAGHa4jy4sQyehollltVBRXFcAAAAOhzB1QS_oUis9rdVHEM6QORhok23TgGyB8wB3oyW40vbyEAKS6HXdD6wWlEtoIzveRyMU-OsH0npvNFBqSJyJ6PQ1sHNqa_XikJtGCMq2tCrHoFioRBLa3Vi42YMAAAAF1aEXv5NaL7GVoGPJAAAAGIwZDg1ODAzLTM4YTAtNDJiMy04MDZlLTdhNGNmOGUxOTZlZQ"
    get_guest_trip_estimate(token, 3.1390, 101.6869, 3.0738, 101.5183)  # KL to Sungai Buloh


# https://sandbox-login.uber.com/oauth/v2/authorize?client_id=G0escxKPepB0kf6U_uKfifx3YeXoPH3z&redirect_uri=http://localhost:8000/callback&scope=ride_widgets&response_type=code