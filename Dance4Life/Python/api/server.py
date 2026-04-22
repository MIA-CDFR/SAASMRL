import threading

from flask import Flask, request, jsonify
import asyncio
import time
from agents.base_sender_agent import BaseSenderAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives, SeververConfig

app = Flask(__name__)


sender_agent = BaseSenderAgent(
    AgentAddresses.API_AGENT,
    AGENT_PASSWORD
)


##Registo Agentes
registered_agents = {}
HEARTBEAT_TIMEOUT = 30  
lock = threading.Lock()

def start_api():
    sender_agent.start_background()
    start_cleanup_thread()
    app.run(host="0.0.0.0", port=SeververConfig.SERVER_PORT, use_reloader=False)


def stop_api():
    sender_agent.stop_background()

pending_match_messages = {}

@app.route('/register_agent', methods=['POST'])
def register_agent():
    data = request.get_json()
    jid = data.get("jid")

    with lock:
        registered_agents[jid] = {
            "last_seen": time.time()
        }

    print(f"[SERVER] Agent registado: {jid}")

    print("Todos os Agentes", registered_agents)
    return jsonify({"status": "registered"})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    jid = data.get("jid")

    with lock:
        if jid in registered_agents:
            registered_agents[jid]["last_seen"] = time.time()
            print("Todos os Agentes", registered_agents)
            return jsonify({"status": "alive"})
        else:
            return jsonify({"status": "not_registered"}), 404
        
   

@app.route('/unregister_agent', methods=['POST'])
def unregister_agent():
    data = request.get_json()
    jid = data.get("jid")

    with lock:
        if jid in registered_agents:
            del registered_agents[jid]
            print(f"[SERVER] Agent removido: {jid}")

    print("Todos os Agentes", registered_agents)

    return jsonify({"status": "unregistered"})

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

        if AgentAddresses.SENSOR_AGENT in registered_agents:
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

        if AgentAddresses.SENSOR_AGENT in registered_agents:
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

def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_agents, daemon=True)
    thread.start()
    print("[SERVER] Cleanup thread iniciada")
    
def cleanup_agents():
    while True:
        now = time.time()
        to_remove = []

        with lock:
            for jid, info in registered_agents.items():
                if now - info["last_seen"] > HEARTBEAT_TIMEOUT:
                    to_remove.append(jid)

            for jid in to_remove:
                print(f"[SERVER] Agent expirado: {jid}")
                del registered_agents[jid]

        time.sleep(10)

if __name__ == '__main__':
    # try:
    #     app.run(host='0.0.0.0', port=5000, debug=True)
    # finally:
    #     sender_agent.stop_background()
    try:
        start_api()
    finally:
        stop_api()