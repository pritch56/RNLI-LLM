import os
import requests
import sys
from datetime import datetime

DATALASTIC_API_KEY = os.environ.get("DATALASTIC_API_KEY")
if not DATALASTIC_API_KEY:
    print("Set DATALASTIC_API_KEY environment variable.")
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
    return data["data"][0]  # Take the first match

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

def main(ship_name):
    # Find ship by name
    ship = find_ship_by_name(ship_name)
    imo = ship.get("imo")
    print(f"Found ship: {ship.get('name')} (IMO: {imo})")

    # Get specs and position
    specs = get_ship_specs(imo)
    pos = get_ship_position(imo)

    # Output required info
    print("\n--- Boat-Specific Data ---")
    print(f"Boat type: {specs.get('type')}")
    print(f"Hull type: {specs.get('hull_type')}")
    print(f"Length: {specs.get('length')}")
    print(f"Beam: {specs.get('breadth')}")
    print(f"Draft: {specs.get('draught')}")
    print(f"Engine type: {specs.get('engine_type')}")
    print(f"Engine power: {specs.get('engine_power')}")
    print(f"Max speed: {specs.get('max_speed')}")
    print(f"Maneuverability: {specs.get('maneuvering_type')}")
    print(f"Weight/load: {specs.get('deadweight')}")
    print(f"Autopilot/nav system: {specs.get('navigation_equipment')}")
    print("\n--- Initial State Data ---")
    print(f"Current position: ({pos.get('current_latitude')}, {pos.get('current_longitude')})")
    print(f"Current speed (knots): {pos.get('speed')}")
    print(f"Current heading (degrees): {pos.get('course')}")
    print(f"Timestamp of current position: {pos.get('timestamp')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python datalastic_ship_info.py <ship_name>")
        sys.exit(1)
    main(sys.argv[1])
