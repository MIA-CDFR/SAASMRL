import requests
from config.config import LAT, LON, OPENAQ_API_KEY

def get_air_quality():
    headers = {"X-API-Key": OPENAQ_API_KEY}

    # Step 1: find nearest monitoring locations
    locations_url = (
        f"https://api.openaq.org/v3/locations"
        f"?coordinates={LAT},{LON}&radius=25000&limit=5"
    )
    loc_resp = requests.get(locations_url, headers=headers)
    loc_data = loc_resp.json()

    if "results" not in loc_data or not loc_data["results"]:
        raise Exception(f"OpenAQ: no locations found near coordinates: {loc_data}")

    # Step 2: get latest readings for the closest location
    location_id = loc_data["results"][0]["id"]

    latest_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
    latest_resp = requests.get(latest_url, headers=headers)
    latest_data = latest_resp.json()

    if "results" not in latest_data or not latest_data["results"]:
        raise Exception(f"OpenAQ: no measurements for location {location_id}: {latest_data}")

    result = {}
    for m in latest_data["results"]:
        param = m.get("parameter", {}).get("name") or m.get("parameter")
        value = m.get("value")
        if param and value is not None:
            result[param] = value

    result["timestamp"] = latest_data["results"][0].get("datetime", {}).get("utc")
    result["location_id"] = location_id
    result["location_name"] = loc_data["results"][0].get("name", "unknown")

    return result