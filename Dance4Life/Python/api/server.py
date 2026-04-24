import threading

from flask import Flask, request, jsonify
import asyncio
import time
from sensor.external_sensors import get_weather
from services.firebase_service import save_invitation
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

users = {}
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

        if AgentAddresses.MATCHING_AGENT in registered_agents:
                future = asyncio.run_coroutine_threadsafe(
                    sender_agent.send_message(
                        payload={"new_data": data, "users": users},
                        agent_to=AgentAddresses.MATCHING_AGENT,
                        performative=AgentPerformatives.REQUEST,
                        ontology=AgentOntologies.MATCHING
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
        print(f"get_user_match {user_id}")

        msgs = pending_match_messages.get(user_id, [])

        print(f"Mensagens pendentes para {user_id}: {msgs}")

        return jsonify(msgs)

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500


@app.route('/set_user_match/<user_id>', methods=['POST'])
def set_user_match(user_id):
    data = request.get_json()
    
    add_invite(user_id, data)  # Exemplo de convite para teste

    return jsonify({"status": "ok"})
#@TODO RR
# [user,invite_id,cluster,aceitou]
# A,1,Moderado,Data,null
# A,1,Moderado,24-04-2026,1->ok
# A,1,Moderado,24-04-2026,0->ok
# A,1,Baixo,Data,null
# A,2,Baixo,Data,null
# A,3,Baixo,Data,null
#cluster_id, 0
#Cluster 0 sem convite, recebe notificação verifica


@app.route('/get_environment_data/<user_id>/<latitude>/<longitude>/<cidade>', methods=['GET'])
def get_environment_data(user_id, latitude, longitude, cidade):

    add_user_profile(user_id, latitude, longitude, cidade)

    weather = get_weather(latitude, longitude, cidade)
    
    data = {
        "temperatura": weather["temperature"],
        "humidade": weather["humidity"],
        "cidade": cidade,
        "latitude": latitude,
        "longitude": longitude
    }

    print(f"Enviar dados ambientais: {data}")

    return jsonify(data)


@app.route('/set_invite_status/<invite_id>/<status_id>', methods=['POST'])
def set_invite_status(invite_id, status_id):
    #@TODO RR data, cluster, 
    print(f"Invite {('aceite' if status_id else 'recusado')}: {invite_id}")

    asyncio.run(save_invitation({
        "invite_id": invite_id,
        "status": status_id
    }))

    return jsonify({"status": "ok"})


def add_user_profile(user_id, latitude, longitude, cidade):
    users[user_id] = {
        "latitude": latitude,
        "longitude": longitude,
        "cidade": cidade
    }


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
