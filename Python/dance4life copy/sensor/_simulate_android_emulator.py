import random
import time
from datetime import UTC, datetime

import requests
from requests.exceptions import ReadTimeout

URL = "http://localhost:5000/collect_data_activities"
# URL = "http://192.168.1.108:5000/collect_data_activities"
# URL = "http://127.0.0.1:5000/collect_data_activities"
REQUEST_TIMEOUT = (3, 20)  # (connect_timeout, read_timeout)


def generate_random_data():
    return {
        "utilizador_id": f"user_{random.randint(1, 5)}",
        "acc": round(random.uniform(0.0, 1.0), 2),
        "hr": random.randint(60, 160),
        "ritmo": round(random.uniform(0.0, 1.0), 2),
        "latitude": round(random.uniform(41.0, 42.0), 6),
        "longitude": round(random.uniform(-8.8, -8.0), 6),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def send_data():
    data = generate_random_data()

    try:
        response = requests.post(URL, json=data, timeout=REQUEST_TIMEOUT)

        print("\nEnviado:")
        print(data)

        print("Resposta:")
        print(response.status_code, response.json())

    except ReadTimeout:
        print(
            "Erro ao enviar: tempo de espera excedido. "
            "Aumente o read timeout ou verifique se o sensor_agent esta bloqueado."
        )
    except Exception as e:
        print(f"Erro ao enviar: {e}")


if __name__ == "__main__":
    print("Simulador Android iniciado...\n")

    while True:
        send_data()
        time.sleep(30)  # envia de 3 em 3 segundos
