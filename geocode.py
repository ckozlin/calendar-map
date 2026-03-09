import requests

def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "calendar-map-script"
    }

    r = requests.get(url, params=params, headers=headers)

    if r.status_code != 200:
        print("Geocode failed:", r.status_code, r.text)
        return None

    data = r.json()

    if not data:
        return None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    return lat, lon