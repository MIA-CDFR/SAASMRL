import requests
from config.config import OPENWEATHER_API_KEY


def get_weather(latitude, longitude):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "timestamp": data["dt"]
    }