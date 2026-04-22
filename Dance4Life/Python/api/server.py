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

pending_match_messages = {}



#OK
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
        return jsonify({"status": "error", "details": str(e)}), 500
    
#TODO Falta implemtação em Android
@app.route('/set_movement_recommendation', methods=['POST'])
def movement_recommendation():
    try:
        data = request.get_json()

        print(f"set_movement_recommendation {data}")
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

#OK
@app.route('/get_user_match/<user_id>', methods=['GET'])
def get_user_match(user_id):
    try:

        msgs = pending_match_messages.get(user_id, [])
        return jsonify(msgs)

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
    
#@TODO alimentar atraves agente APP Cluster->Agente->API
@app.route('/set_user_match/<user_id>', methods=['POST'])
def set_user_match(user_id):
    data = request.get_json()

    add_invite(user_id, data)  # Exemplo de convite para teste

    return jsonify({"status": "ok"})

#@TODO vai consultar a API
@app.route('/get_environment_data/<user_id>/<latitude>/<longitude>/<cidade>', methods=['GET'])
def get_environment_data(user_id, latitude, longitude, cidade):
    data = {
        "temperatura": 25.5,
        "humidade": 68,
        "cidade": cidade,
        "latitude": latitude,
        "longitude": longitude
    }

    print(f"Enviar dados ambientais: {data}")

    return jsonify(data)

#@TODO falta guardar no firebase
@app.route('/set_invite_status/<invite_id>/<status_id>', methods=['POST'])
def set_invite_status(invite_id, status_id):

    print(f"Invite {('aceite' if status_id else 'recusado')}: {invite_id}")

    return jsonify({"status": "ok"})


def add_invite(user_id, data):
    print(f"userID {user_id} data {data}")
    if user_id not in pending_match_messages:
        pending_match_messages[user_id] = []

    pending_match_messages[user_id].append(data)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        sender_agent.stop_background()