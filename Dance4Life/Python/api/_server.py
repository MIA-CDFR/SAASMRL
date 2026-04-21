import random

from flask import Flask, request, jsonify
import asyncio
from pydantic import ValidationError
from agents.api_agent import ApiAgent
from model.data_model import SensorActivityData
from spade.template import Template

app = Flask(__name__)

api_agent = None
sensor_loop = None

def init_agent(agent, loop):
    global api_agent, sensor_loop
    api_agent = agent
    sensor_loop = loop
    print("ApiAgent e sensor_loop inicializados")


def send_data_to_sensor_agent(data):
    global api_agent, sensor_loop

    if api_agent is None or sensor_loop is None:
        print("ApiAgent ou sensor_loop não inicializados")
        return False

    async def run():
        future = sensor_loop.create_future()

        behaviour = api_agent.RequestBehaviourSendSensorActivityToSensor(
            ontology="sensor_activity",
            data=data,
            receiver="sensor_agent@localhost",
            future=future
        )

        template = Template()
        template.set_metadata("conversation-id", behaviour.conversation_id)

        api_agent.add_behaviour(behaviour, template)        

        return await asyncio.wait_for(future, timeout=15)

    try:
        future = asyncio.run_coroutine_threadsafe(run(), sensor_loop)
        return future.result(timeout=20)
    except Exception as e:
        print("Erro:", e)
        return False
    

@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    try:
        data = request.json
        #SensorActivityData

        print("\nDados recebidos:")
        print(data)

        sensor_data = SensorActivityData(**data)
        print(sensor_data)
        
        sent = send_data_to_sensor_agent(sensor_data)
        
        if not sent:
            return jsonify({"status": "agent_not_ready"}), 503

        return jsonify({"status": "ok"}), 200

    except ValidationError as e:
        return jsonify({
            "status": "error",
            "details": e.errors()
        }), 400

pending_messages = {}


def add_invite(user_id, invite_id, from_user):
    if user_id not in pending_messages:
        pending_messages[user_id] = []

    pending_messages[user_id].append({
        "type": "invite",
        "id": invite_id,
        "user": from_user
    })

@app.route('/get_updates/<user_id>', methods=['GET'])
def get_updates(user_id):
    add_invite(user_id, f"invite{random.randint(1000, 9999)}", f"user{random.randint(1000, 9999)}")  # Exemplo de convite para teste
    msgs = pending_messages.get(user_id, [])

    # limpar depois de enviar
    pending_messages[user_id] = []
    print(f"Enviando mensagens para {user_id}: {msgs}")

    return jsonify(msgs)

@app.route('/accept_invite', methods=['POST'])
def accept_invite():
    data = request.json
    invite_id = data.get("inviteId")

    print(f"Invite aceite: {invite_id}")

    return jsonify({"status": "ok"})

@app.route('/reject_invite', methods=['POST'])
def reject_invite():
    data = request.json
    invite_id = data.get("inviteId")

    print(f"Invite rejeitado: {invite_id}")

    return jsonify({"status": "ok"})