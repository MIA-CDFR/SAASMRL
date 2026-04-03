import asyncio
import threading

from agents.sensor_agent import SensorAgent

import api.server as server
from messaging.to_sensor_agent import start_bridge


def start_flask():
    server.app.run(host="0.0.0.0", port=5000, use_reloader=False)


async def _start_agent(agent):
    start_result = agent.start()
    if asyncio.iscoroutine(start_result):
        await start_result
    else:
        start_result.result()


async def _stop_agent(agent):
    stop_result = agent.stop()
    if asyncio.iscoroutine(stop_result):
        await stop_result


async def run():
    # criar agente
    sensor_agent = SensorAgent("sensor_agent@localhost", "password")
    # sensor_agent = SensorAgent("sensor_agent@mia.lan", "password")
    # sensor_agent = SensorAgent("sensor_agent@mia.lan", "password", host="localhost", port=5222)

    # iniciar agente
    await _start_agent(sensor_agent)

    print("Agente iniciado")

    # 🔗 ligar Flask ao SPADE (BRIDGE CORRETO)
    start_bridge(sensor_agent, asyncio.get_running_loop())

    # iniciar Flask
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    print("Servidor Flask iniciado")

    # manter app viva
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await _stop_agent(sensor_agent)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("A encerrar...")
