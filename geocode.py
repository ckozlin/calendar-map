import requests
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
CACHE_FILE = "geocode_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


cache = load_cache()


def geocode(address):
    if address in cache:
        print("Using cached coords:", address)
        return tuple(cache[address])

    url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address": address,
        "key": API_KEY,
    }

    print("Geocoding via Google:", address)
    r = requests.get(url, params=params)
    data = r.json()
    time.sleep(1)

    if data["status"] != "OK":
        print("Geocode failed:", address, data["status"])
        return None

    location = data["results"][0]["geometry"]["location"]

    coords = (location["lat"], location["lng"])

    cache[address] = coords
    save_cache(cache)

    return coords