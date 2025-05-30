# import webbrowser
# import urllib.parse

# base_url = "https://auth.uber.com/oauth/v2/authorize"
# params = {
#     "client_id": "",  # Replace with your actual client ID
#     "response_type": "code",
#     "scope": "profile",
#     "redirect_uri": "https://yourapp.com/callback"  # Replace with your redirect URI
# }

# auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
# webbrowser.open(auth_url)

import requests

url = "https://sandbox-login.uber.com/oauth/v2/token"

data = {
    'client_id': 'G0escxKPepB0kf6U_uKfifx3YeXoPH3z',
    'client_secret': 'iJ8nbj0duTjx6pzS2T6sxTyplu94GrDNM1k6-D7s',
    'grant_type': 'client_credentials',
    'scope': 'guests.trips'  # Replace this with actual scopes
}


response = requests.post(url, data=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
