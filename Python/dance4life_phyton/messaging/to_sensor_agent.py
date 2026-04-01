import uuid

from spade.message import Message
import asyncio
import json

from agents import sensor_agent
# def send_data_to_sensor_agent(agent, loop, jid, data):

#     async def send():
#         msg = Message(to=jid)

#         msg.set_metadata("performative", "inform")
#         msg.set_metadata("ontology", "sensor-data")
#         msg.set_metadata("language", "json")

#         msg.body = json.dumps(data)

#         await agent.send(msg)

#     asyncio.run_coroutine_threadsafe(send(), loop)
from flask import Flask, request, jsonify
import asyncio
import uuid
import json

from spade.message import Message
from spade.behaviour import CyclicBehaviour

app = Flask(__name__)

# =========================
# CONFIGURAÇÃO GLOBAL
# =========================

sensor_agent = None
sensor_agent_loop = None
sensor_agent_jid = "sensor_agent@localhost"

pending_requests = {}


# =========================
# CRIAR FUTURE NO LOOP CERTO
# =========================

async def create_future():
    loop = asyncio.get_running_loop()
    return loop.create_future()


# =========================
# ENVIO DE DADOS PARA AGENTE
# =========================

def send_data_to_sensor_agent(data):
    if sensor_agent is None or sensor_agent_loop is None:
        print("⚠️ Agente não está pronto")
        return None

    conversation_id = str(uuid.uuid4())

    # criar future no loop do SPADE
    future = asyncio.run_coroutine_threadsafe(
        create_future(), sensor_agent_loop
    ).result()

    pending_requests[conversation_id] = future

    async def send():
        msg = Message(to=sensor_agent_jid)

        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "sensor-data")
        msg.set_metadata("conversation-id", conversation_id)

        # opcional (recomendado)
        msg.thread = conversation_id

        msg.body = json.dumps(data)

        await sensor_agent.send(msg)

        print(f"📤 Enviado para agente ({conversation_id})")

    # enviar no loop correto
    asyncio.run_coroutine_threadsafe(send(), sensor_agent_loop)

    try:
        result = future.result(timeout=10)
        print(f"✅ Resposta recebida ({conversation_id})")
        return result

    except Exception as e:
        print(f"❌ Timeout ou erro: {e}")
        pending_requests.pop(conversation_id, None)
        return None


# =========================
# BEHAVIOUR PARA RECEBER RESPOSTAS
# =========================

class ResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
            conv_id = msg.get_metadata("conversation-id")
            performative = msg.get_metadata("performative")

            print(f"📩 Reply recebido ({performative}) - {conv_id}")

            if conv_id in pending_requests:
                future = pending_requests.pop(conv_id)

                if not future.done():
                    future.set_result(msg.body)


# =========================
# ENDPOINT FLASK
# =========================

@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    data = request.json

    print("\n📥 Dados recebidos no Flask:")
    print(data)

    response = send_data_to_sensor_agent(data)

    if response is None:
        return jsonify({"status": "timeout"}), 504

    try:
        return jsonify(json.loads(response)), 200
    except Exception:
        return jsonify({"raw_response": response}), 200


# =========================
# FUNÇÃO PARA INICIAR BRIDGE
# =========================

def start_bridge(agent, loop):
    global sensor_agent, sensor_agent_loop

    sensor_agent = agent
    sensor_agent_loop = loop

    # adicionar behaviour para receber respostas
    agent.add_behaviour(ResponseBehaviour())

    print("🔗 Bridge Flask <-> SPADE iniciada")


# =========================
# MAIN (EXEMPLO)
# =========================

if __name__ == "__main__":
    app.run(port=5000, debug=True)