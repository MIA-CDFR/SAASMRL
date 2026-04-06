import asyncio
import threading
from spade.presence import PresenceType, PresenceShow
from agents.sensor_agent import SensorAgent
from agents.api_agent import ApiAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.har_agent import HARAgent
from agents.environment_agent import EnvironmentAgent
from agents.database_agent import DatabaseAgent

#from matching_agent import MatchingAgent

import api.server as server


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
    coordinator_agent = CoordinatorAgent("coordinator_agent@localhost", "password")
    sensor_agent = SensorAgent("sensor_agent@localhost", "password")
    api_agent = ApiAgent("api_agent@localhost", "password")
    har_agent = HARAgent("har_agent@localhost", "password")
    environment_agent = EnvironmentAgent("environment_agent@localhost", "password")
    database_agent = DatabaseAgent("database_agent@localhost", "password")


    # iniciar agentes
    await _start_agent(coordinator_agent)
    await _start_agent(sensor_agent)
    await _start_agent(api_agent)
    await _start_agent(har_agent)
    await _start_agent(environment_agent)
    await _start_agent(database_agent)
    #await _start_agent(matching_agent)

    coordinator_agent.web.start(hostname="127.0.0.1", port="10000")
    sensor_agent.web.start(hostname="127.0.0.1", port="10001")
    api_agent.web.start(hostname="127.0.0.1", port="10002")
    har_agent.web.start(hostname="127.0.0.1", port="10003")
    environment_agent.web.start(hostname="127.0.0.1", port="10004")
    database_agent.web.start(hostname="127.0.0.1", port="10005")


    # coordinator_agent.presence.set_presence(
    #                             presence_type=PresenceType.AVAILABLE,  # set availability
    #                             show=PresenceShow.CHAT,  # show status
    #                             status="Lunch",  # status message
    #                             priority=2  # connection priority
    #                             )
    # sensor_agent.presence.set_presence(
    #                             presence_type=PresenceType.AVAILABLE,  # set availability
    #                             show=PresenceShow.CHAT,  # show status
    #                             status="Lunch",  # status message
    #                             priority=2  # connection priority
    #                             )
    # api_agent.presence.set_presence(
    #                             presence_type=PresenceType.AVAILABLE,  # set availability
    #                             show=PresenceShow.CHAT,  # show status
    #                             status="Lunch",  # status message
    #                             priority=2  # connection priority
    #                             )
    #contact = api_agent.presence.get_contact("sensor_agent@localhost")

    print("Agentes iniciados")

    # ligar Flask ao ApiAgent
    #server.sensor_agent = sensor_agent
    loop = asyncio.get_running_loop()
    server.init_agent(api_agent, loop)

    #server.api_agent = api_agent
    #server.sensor_loop = asyncio.get_running_loop()
    #server.sensor_agent_loop = asyncio.get_running_loop()

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
        await _stop_agent(api_agent)
        await _stop_agent(coordinator_agent)
     #   await _stop_agent(matching_agent)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("A encerrar...")
