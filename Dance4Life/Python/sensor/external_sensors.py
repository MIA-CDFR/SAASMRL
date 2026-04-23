import requests
from config.config import OPENWEATHER_API_KEY


def get_weather_v0(latitude, longitude):
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


import requests

def get_weather(latitude=None, longitude=None, cidade=None):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Lógica de decisão dos parâmetros
    if cidade:
        # Se cidade for fornecida, ignoramos as coordenadas
        params = f"q={cidade}"
    elif latitude is not None and longitude is not None:
        # Caso contrário, usamos as coordenadas
        params = f"lat={latitude}&lon={longitude}"
    else:
        return {"error": "Deves fornecer uma cidade ou coordenadas (lat/lon)."}

    url = f"{base_url}?{params}&appid={OPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url)
    
    # Verificar se a API respondeu com sucesso antes de processar os dados
    if response.status_code != 200:
        return {"error": f"Erro na API: {response.status_code}", "message": response.json().get("message")}

    data = response.json()


    return {
        "city_name": data.get("name"), # Útil para confirmar que cidade a API encontrou
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "timestamp": data["dt"]
    }