import signal
import sys

from agents.database_agent import DatabaseAgent
from agents.environment_agent import EnvironmentAgent
from agents.har_agent import HarAgent
from api.server import start_api, stop_api
from agents.sensor_agent import SensorAgent
from agents.coordinator_agent import CoordinatorAgent
from config.config import AgentAddresses

import asyncio


def start_spade_agents():
    sensor_agent = SensorAgent(AgentAddresses.SENSOR_AGENT, "password")
    sensor_agent.start_background()

    coordinator_agent = CoordinatorAgent(AgentAddresses.COORDINATOR_AGENT, "password")
    coordinator_agent.start_background()

    environment_agent = EnvironmentAgent(AgentAddresses.ENVIRONMENT_AGENT, "password")
    environment_agent.start_background()

    har_agent = HarAgent(AgentAddresses.HAR_AGENT, "password")
    har_agent.start_background()

    database_agent = DatabaseAgent(AgentAddresses.DATABASE_AGENT, "password")
    database_agent.start_background()

    print("SPADE agents iniciados")

    return sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent


def stop_spade_agents(sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent):
    sensor_agent.stop_background()
    coordinator_agent.stop_background()
    environment_agent.stop_background()
    har_agent.stop_background()
    database_agent.stop_background()

    print("***SPADE agents parados")


def main():
    sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent = start_spade_agents()

    # def shutdown(sig, frame):
    #     print("\nA parar aplicação...")
    #     stop_api()
    #     stop_spade_agents(sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent)
    #     sys.exit(0)

    # signal.signal(signal.SIGINT, shutdown)
    # signal.signal(signal.SIGTERM, shutdown)

    try:
        start_api()
    finally:
        stop_spade_agents(sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent)

if __name__ == '__main__':
    main()
