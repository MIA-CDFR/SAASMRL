import datetime
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
user_clusters = {}

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
            #print("Todos os Agentes", registered_agents)
            #print("Todos os Agentes", registered_agents)
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
            #print(f"[SERVER] Agent removido: {jid}")

    #print("Todos os Agentes", registered_agents)

    return jsonify({"status": "unregistered"})


@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    try:
        data = request.get_json()
        data["date"] = get_actual_datetime()

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
        #print("\nAgentAddresses.SENSOR_AGENT:")
        
        asyncio.sleep(5)
        
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
        #print("\nAgentAddresses.MATCHING_AGENT:")
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
        data["date"] = get_actual_datetime()
        #print(f"set_movement_recommendation {data}")
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

@app.route('/get_user_match/<user_id>', methods=['GET'])
def get_user_match(user_id):
    try:
        print(f"get_user_match {user_id}")

        msgs = pending_match_messages.get(user_id, [])

        print(f"------------------Mensagens pendentes para {user_id}: {msgs}")
        print(f"------------------user_clusters {user_clusters}")

        return jsonify(msgs), 200

    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

@app.route('/set_user_match/<user_id>', methods=['POST'])
def set_user_match(user_id):
    data = request.get_json()
    
    add_invite(user_id, data)

    return jsonify({"status": "ok"})

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

    #print(f"Enviar dados ambientais: {data}")

    return jsonify(data)

@app.route('/set_invite_status/<invite_id>/<status_id>', methods=['POST'])
def set_invite_status(invite_id, status_id):
    try:
        status = status_id == "true"
        user_found = None

        #print(f"Invite {'aceite' if status else 'recusado'}: {invite_id}")

        # procurar invite
        for user_id, invite_list in pending_match_messages.items():

            if not invite_list:
                continue
            
            if status:
                user_clusters[user_id] = {
                    "cluster": invite_list[0].get("cluster"),
                    "date": get_actual_date()
                }
                pending_match_messages[user_id] = []  # limpar mensagens pendentes

            invite = invite_list[0]

            if (
                invite.get("id") == invite_id and
                invite.get("status") is None
            ):
                invite["status"] = status
                user_found = user_id

                #print(f"[UPDATE] {user_id} → {invite}")
                break

        # async save
        asyncio.run(save_invitation({
            "invite_id": invite_id,
            "userId": user_found,
            "status": status,
            "date": get_actual_datetime()
        }))

        return jsonify({"status": "ok"})

    except Exception as e:
        #print(f"[ERROR] {e}")
        return jsonify({"status": "error"}), 500

def add_user_profile(user_id, latitude, longitude, cidade):
    users[user_id] = {
        "latitude": latitude,
        "longitude": longitude,
        "cidade": cidade
    }

def add_invite(user_id, data):
    #print(f"add_invite userID {user_id} data {data}")

    print(f"++++++++++++++++add_invite userID {user_id} data {data}")
    print(f"++++++++++++++++user_clusters {user_clusters}")

    if user_id not in pending_match_messages or not (
        user_id in user_clusters and
        user_clusters[user_id]["cluster"] == data.get("cluster") and
        user_clusters[user_id]["date"] == get_actual_date()
    ):
        pending_match_messages[user_id] = [data]

        print(f"pending_match_messages {pending_match_messages}")

    print(f"-------------pending_match_messages userID {user_id} {pending_match_messages}")

def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_agents, daemon=True)
    thread.start()
    #print("[SERVER] Cleanup thread iniciada")


def cleanup_agents():
    while True:
        now = time.time()
        to_remove = []

        with lock:
            for jid, info in registered_agents.items():
                if now - info["last_seen"] > HEARTBEAT_TIMEOUT:
                    to_remove.append(jid)

            for jid in to_remove:
                #print(f"[SERVER] Agent expirado: {jid}")
                del registered_agents[jid]

        time.sleep(10)

def get_actual_datetime():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")

def get_actual_date():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y")

if __name__ == '__main__':
    try:
        start_api()
    finally:
        stop_api()
