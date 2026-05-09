import signal
import sys
import threading
import time
import os
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from agents.database_agent import DatabaseAgent
from agents.environment_agent import EnvironmentAgent
from agents.har_agent import HarAgent
from api.server import start_api
from agents.sensor_agent import SensorAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.matching_agent import ClusteringAgent
from config.config import AgentAddresses, AGENT_PASSWORD


def start_spade_agents():
    sensor_agent = SensorAgent(AgentAddresses.SENSOR_AGENT, AGENT_PASSWORD)
    sensor_agent.start_background()

    coordinator_agent = CoordinatorAgent(AgentAddresses.COORDINATOR_AGENT, AGENT_PASSWORD)
    coordinator_agent.start_background()

    environment_agent = EnvironmentAgent(AgentAddresses.ENVIRONMENT_AGENT, AGENT_PASSWORD)
    environment_agent.start_background()

    har_agent = HarAgent(AgentAddresses.HAR_AGENT, AGENT_PASSWORD)
    har_agent.start_background()

    database_agent = DatabaseAgent(AgentAddresses.DATABASE_AGENT, AGENT_PASSWORD)
    database_agent.start_background()

    clustering_agent = ClusteringAgent(AgentAddresses.MATCHING_AGENT, AGENT_PASSWORD)
    clustering_agent.start_background()


    print("SPADE agents iniciados")

    return sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent, clustering_agent


def stop_spade_agents(sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent, clustering_agent):
    sensor_agent.stop_background()
    coordinator_agent.stop_background()
    environment_agent.stop_background()
    har_agent.stop_background()
    database_agent.stop_background()
    clustering_agent.stop_background()

    print("***SPADE agents parados")

def start_dashboard_server():

    dashboard_path = os.path.abspath(
        os.path.join(os.getcwd(), "../D3_web")
    )

    print("CURRENT:", os.getcwd())
    print("DASHBOARD PATH:", dashboard_path)
    print("EXISTS:", os.path.exists(dashboard_path))

    from functools import partial
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

    handler = partial(
        SimpleHTTPRequestHandler,
        directory=dashboard_path
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", 8000),
        handler
    )

    print("[DASHBOARD] http://localhost:8000/dashboard.html")

    server.serve_forever()

def main():

    dashboard_thread = threading.Thread(
        target=start_dashboard_server,
        daemon=True
    )
    dashboard_thread.start()
        
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    print("[MAIN] A aguardar server arrancar...")
    time.sleep(3)
    print("[MAIN] Arrancar agentes...")
    sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent, clustering_agent = start_spade_agents()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] A desligar...")

        stop_spade_agents(
            sensor_agent,
            coordinator_agent,
            environment_agent,
            har_agent,
            database_agent,
            clustering_agent
        )
    # try:
    #     start_api()
    # finally:
    #     stop_spade_agents(sensor_agent, coordinator_agent, environment_agent, har_agent, database_agent, matching_agent)

if __name__ == '__main__':
    main()
