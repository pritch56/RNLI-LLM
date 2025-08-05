import os
import sys
import requests

DATALASTIC_API_KEY = os.environ.get("DATALASTIC_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

if not DATALASTIC_API_KEY or not OPENWEATHER_API_KEY:
    print("Set DATALASTIC_API_KEY and OPENWEATHER_API_KEY environment variables.")
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

def get_ship_specs(imo):
    url = f"{BASE_URL}/vessel"
    params = {"api_key": DATALASTIC_API_KEY, "imo": imo}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("data", {})

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

def main(ship_name):
    # --- Boat Data ---
    ship = find_ship_by_name(ship_name)
    imo = ship.get("imo")
    specs = get_ship_specs(imo)
    pos = get_ship_position(imo)

    print("⚓ 1. Boat-Specific Data")
    print(f"Boat name: {ship.get('name')}")
    print(f"Boat type: {specs.get('type')}")
    print(f"Hull type: {specs.get('hull_type')}")
    print(f"Length: {specs.get('length')} m")
    print(f"Beam: {specs.get('breadth')} m")
    print(f"Draft: {specs.get('draught')} m")
    print(f"Engine type: {specs.get('engine_type')}")
    print(f"Engine power: {specs.get('engine_power')} kW")
    print(f"Max speed: {specs.get('max_speed')} knots")
    print(f"Maneuverability: {specs.get('maneuvering_type')}")
    print(f"Weight/load: {specs.get('deadweight')} tons")
    print(f"Autopilot/nav system: {specs.get('navigation_equipment')}")

    print("\n🌍 2. Initial State Data")
    lat = pos.get('current_latitude')
    lon = pos.get('current_longitude')
    print(f"Current position: ({lat}, {lon})")
    print(f"Current speed (knots): {pos.get('speed')}")
    print(f"Current heading (degrees): {pos.get('course')}")
    print(f"Timestamp of current position: {pos.get('timestamp')}")

    print("\n🌊 3. Environmental Conditions")
    if lat and lon:
        weather = get_weather(lat, lon)
        wind = weather.get("wind", {})
        mainw = weather.get("main", {})
        print(f"Wind speed: {wind.get('speed')} m/s, direction: {wind.get('deg')}°")
        print(f"Temperature: {mainw.get('temp')}°C")
        # Placeholders for additional data sources:
        print("Wave height and direction: [Requires marine API, e.g., StormGlass, Copernicus]")
        print("Current (oceanic) speed and direction: [Requires ocean current API]")
        print("Tides (level and direction): [Requires tide API]")
        print("Water depth (bathymetry): [Requires bathymetry API]")
        print("Salinity: [Requires oceanographic API]")
        print(f"Weather systems: {weather.get('weather', [{}])[0].get('description')}")
    else:
        print("No valid position for environmental data.")

    print("\n🗺️ 4. Navigational Constraints")
    print("Landmasses, ports, shipping lanes, no-go zones, traffic, canals, regulatory zones: [Requires map/geofencing APIs, e.g., OpenSeaMap, MarineTraffic]")

    print("\n🧭 5. Navigational Behavior and Intent")
    print("AIS historical tracks, planned route, past route patterns, destination, crew behavior: [Requires AIS history and planning data]")

    print("\n🛰️ 6. Data Sources / Integration")
    print("AIS: Datalastic | Weather: OpenWeatherMap | Others: [Integrate additional APIs as needed]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python realtime_boat_data.py <ship_name>")
        sys.exit(1)
    main(sys.argv[1])
