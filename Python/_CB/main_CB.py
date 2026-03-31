from agents.coordinator_agent import CoordinatorAgent
from api.server import app
import api.server as server


if __name__ == "__main__":
    coordinator = CoordinatorAgent()

    server.coordinator = coordinator

    print("Sistema iniciado 🚀")

    app.run(host="0.0.0.0", port=5000)