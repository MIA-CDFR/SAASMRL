import requests
from config.config import TOMTOM_API_KEY, LAT, LON

def get_traffic():
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={LAT},{LON}&key={TOMTOM_API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    flow = data["flowSegmentData"]
    
    return {
        "current_speed": flow["currentSpeed"],
        "free_flow_speed": flow["freeFlowSpeed"],
        "confidence": flow["confidence"],
        "timestamp": flow["currentTravelTime"]
    }