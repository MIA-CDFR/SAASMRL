import requests
import random
import time
import argparse
import datetime

BASE_URL = "http://localhost:5000"


def timestamp():
    return datetime.datetime.now(datetime.UTC).isoformat()


def gerar_dados_collect(device_id: str = None) -> dict:
    return {
        "device_id": device_id or f"device-{random.randint(1, 999):03d}",
        "acc": round(random.uniform(0.0, 2.0), 4),
        "hr": round(random.uniform(55.0, 135.0), 2),
        "ritmo": round(random.uniform(0.5, 2.5), 4),
        "latitude": round(random.uniform(41.0, 42.5), 6),
        "longitude": round(random.uniform(-8.8, -7.6), 6),
    }


def gerar_dados_movement(device_id: str = None) -> dict:
    return {
        "device_id": device_id or f"device-{random.randint(1, 999):03d}",
        "acc": round(random.uniform(0.0, 2.0), 4),
        "hr": round(random.uniform(55.0, 140.0), 2),
        "latitude": round(random.uniform(41.0, 42.5), 6),
        "longitude": round(random.uniform(-8.8, -7.6), 6),
    }


def gerar_dados_matching(device_id: str = None) -> dict:
    return {
        "device_id": device_id or f"device-{random.randint(1, 999):03d}",
        "cluster_id": f"cluster_{random.randint(1, 5)}",
        "timestamp": timestamp(),
    }


def enviar(payload: dict, url: str) -> None:
    print(f"\n→ A enviar para {url}")
    print(f"  Payload: {payload}")

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"  Status : {response.status_code}")
        print(f"  Resposta: {response.json()}")

    except requests.exceptions.ConnectionError:
        print("  ERRO: Não foi possível ligar ao servidor.")
    except requests.exceptions.Timeout:
        print("  ERRO: Timeout — servidor demorou demasiado.")
    except Exception as e:
        print(f"  ERRO: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador multi-endpoint"
    )

    parser.add_argument(
        "--intervalo", type=float, default=10.0,
        help="Segundos entre envios (default: 10)"
    )

    parser.add_argument(
        "--device-id", default=None,
        help="ID fixo do dispositivo (default: aleatório)"
    )

    parser.add_argument(
        "--modo",
        choices=["auto", "collect", "movement", "matching"],
        default="auto",
        help="auto = envia para todos os endpoints"
    )

    args = parser.parse_args()

    url_collect = f"{BASE_URL}/collect_data_activities"
    url_movement = f"{BASE_URL}/movement_recommendation"
    url_matching = f"{BASE_URL}/matching"

    print(f"Simulador iniciado (modo: {args.modo})")
    print("Ctrl+C para parar.\n")

    i = 1
    while True:
        print(f"\n[#{i}]")

        if args.modo in ["auto", "collect"]:
            payload_collect = gerar_dados_collect(args.device_id)
            enviar(payload_collect, url_collect)

        if args.modo in ["auto", "movement"]:
            payload_movement = gerar_dados_movement(args.device_id)
            enviar(payload_movement, url_movement)

        if args.modo in ["auto", "matching"]:
            payload_matching = gerar_dados_matching(args.device_id)
            enviar(payload_matching, url_matching)

        i += 1
        time.sleep(args.intervalo)


if __name__ == "__main__":
    main()