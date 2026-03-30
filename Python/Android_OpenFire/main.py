import asyncio
import threading

from sensor_agent import SensorAgent
from matching_agent import MatchingAgent

import server


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
    # criar agentes
    sensor_agent = SensorAgent("sensor_agent@localhost", "password")
    matching_agent = MatchingAgent("matching_agent@localhost", "password")

    # iniciar agentes
    await _start_agent(sensor_agent)
    await _start_agent(matching_agent)

    print("Agentes iniciados")

    # ligar Flask ao SensorAgent (MUITO IMPORTANTE)
    server.sensor_agent = sensor_agent
    server.sensor_agent_jid = "sensor_agent@localhost"
    server.sensor_agent_loop = asyncio.get_running_loop()

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
        await _stop_agent(matching_agent)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("A encerrar...")
