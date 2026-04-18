from flask import Flask, request, jsonify
import asyncio

from agents.base_sender_agent import BaseSenderAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives

app = Flask(__name__)


sender_agent = BaseSenderAgent(
    AgentAddresses.API_AGENT,
    AGENT_PASSWORD
)

def start_api():
    sender_agent.start_background()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


def stop_api():
    sender_agent.stop_background()



@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "details": "Body JSON inválido ou vazio"
            }), 400

        print("\nDados recebidos:")
        print(data)

        future = asyncio.run_coroutine_threadsafe(
            sender_agent.send_message(
                payload=data,
                agent_to=AgentAddresses.SENSOR_AGENT,
                performative=AgentPerformatives.REQUEST,
                ontology=AgentOntologies.SENSOR_ACTIVITY
            ),
            sender_agent.agent_loop
        )

        future.result()

        return jsonify({
            "status": "ok",
            "message": "Dados enviados para o Sensor Agent"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "details": str(e)
        }), 500

@app.route('/movement_recommendation', methods=['POST'])
def movement_recommendation():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error"}), 400

        future = asyncio.run_coroutine_threadsafe(
            sender_agent.send_message(
                payload=data,
                agent_to=AgentAddresses.SENSOR_AGENT,
                performative=AgentPerformatives.REQUEST,
                ontology=AgentOntologies.MOVEMENT_RECOMMENDATION
            ),
            sender_agent.agent_loop
        )

        future.result()

        return jsonify({
            "status": "ok",
            "message": "Dados enviados para o Sensor Agent"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
    
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        sender_agent.stop_background()