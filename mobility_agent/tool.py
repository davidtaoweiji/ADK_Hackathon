import requests
api_key='AIzaSyBVMS-qnZebtj6QzeAy6HDbwCDyFIzD0XA'
def estimate_travel_time(start, destination, mode):
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
    
def get_weather(address):
    lat, lng = geocode_address(address, api_key)
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


if __name__ == "__main__":
    # start_location = "Space Karaoke Bar & Cafe"
    # destination_location = "CBRE Richardson"
    # travel_mode = "driving"  # Options: 'driving', 'walking
    # distance = estimate_travel_time(start_location, destination_location, travel_mode)
    # print(f"Estimated travel time from {start_location} to {destination_location} by {travel_mode}: {distance}")
    print(f"Weather at: {get_weather("CBRE Richardson")}")
