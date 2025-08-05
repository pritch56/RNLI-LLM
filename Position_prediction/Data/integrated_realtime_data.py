import os
import sys
import requests
from datetime import datetime

# --- API KEYS ---
DATALASTIC_API_KEY = os.environ.get("DATALASTIC_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WORLDTIDES_API_KEY = os.environ.get("WORLDTIDES_API_KEY")
COPERNICUS_USERNAME = os.environ.get("COPERNICUS_USERNAME")
COPERNICUS_PASSWORD = os.environ.get("COPERNICUS_PASSWORD")

if not DATALASTIC_API_KEY or not OPENWEATHER_API_KEY or not WORLDTIDES_API_KEY or not COPERNICUS_USERNAME or not COPERNICUS_PASSWORD:
    print("Set DATALASTIC_API_KEY, OPENWEATHER_API_KEY, WORLDTIDES_API_KEY, COPERNICUS_USERNAME, and COPERNICUS_PASSWORD environment variables.")
    sys.exit(1)

BASE_URL = "https://api.datalastic.com/api/v0"

def find_ship_by_name(ship_name):
    url = f"{BASE_URL}/vessel_search"
    params = {"api_key": DATALASTIC_API_KEY, "search": ship_name}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("data"):
        raise Exception("No ship found with that name.")
    return data["data"][0]

def get_ship_position(imo):
    url = f"{BASE_URL}/vessel_real_time"
    params = {"api_key": DATALASTIC_API_KEY, "imo": imo}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("data", {})

def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_ocean_current(lat, lon):
    # Copernicus Marine API: Use latest product for demonstration (surface currents)
    # This is a simplified example using the OPeNDAP subset service for demonstration.
    # For production, use the copernicusmarine python package or their REST API.
    # Here, we just print the URL for the user to fetch data manually.
    print(f"Copernicus Marine: Surface current data for ({lat},{lon}) can be accessed via their API.")
    print("See: https://data.marine.copernicus.eu/products")
    return {}

def get_tides(lat, lon):
    url = "https://www.worldtides.info/api/v3"
    params = {
        "heights": "",
        "lat": lat,
        "lon": lon,
        "key": WORLDTIDES_API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_map_tile_url(lat, lon, zoom=12):
    # OpenSeaMap tile server (for visualization, not data API)
    # Convert lat/lon to tile x/y (slippy map tiling)
    import math
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    url = f"https://tiles.openseamap.org/seamark/{zoom}/{xtile}/{ytile}.png"
    return url

def main(ship_name):
    # --- AIS Data ---
    ship = find_ship_by_name(ship_name)
    imo = ship.get("imo")
    pos = get_ship_position(imo)
    lat = pos.get('current_latitude')
    lon = pos.get('current_longitude')
    print("AIS Data:")
    print(f"  Name: {ship.get('name')}")
    print(f"  Position: ({lat}, {lon})")
    print(f"  Speed: {pos.get('speed')} knots")
    print(f"  Heading: {pos.get('course')}°")
    print(f"  Timestamp: {pos.get('timestamp')}\n")

    # --- Weather Data ---
    if lat and lon:
        weather = get_weather(lat, lon)
        wind = weather.get("wind", {})
        print("Weather Data (OpenWeatherMap):")
        print(f"  Wind speed: {wind.get('speed')} m/s, direction: {wind.get('deg')}°")
        print(f"  Temperature: {weather.get('main',{}).get('temp')}°C")
        print(f"  Weather: {weather.get('weather',[{}])[0].get('description')}\n")
    else:
        print("No valid position for weather data.\n")

    # --- Ocean Current Data ---
    if lat and lon:
        get_ocean_current(lat, lon)
        print()
    else:
        print("No valid position for ocean current data.\n")

    # --- Tide Data ---
    if lat and lon:
        tides = get_tides(lat, lon)
        print("Tide Data (WorldTides):")
        for h in tides.get("heights", []):
            t = datetime.utcfromtimestamp(h["dt"]).strftime('%Y-%m-%d %H:%M UTC')
            print(f"  {t}: {h['height']} m")
        print()
    else:
        print("No valid position for tide data.\n")

    # --- Map/Geofencing Data ---
    if lat and lon:
        tile_url = get_map_tile_url(float(lat), float(lon))
        print("Map/Geofencing (OpenSeaMap):")
        print(f"  Tile URL for visualization: {tile_url}\n")
    else:
        print("No valid position for map/geofencing data.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python integrated_realtime_data.py <ship_name>")
        sys.exit(1)
    main(sys.argv[1])
