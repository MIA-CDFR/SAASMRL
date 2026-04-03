import uuid
import asyncio
import json

from spade.message import Message
from spade.behaviour import CyclicBehaviour
from spade.template import Template

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

        msg.thread = conversation_id
        msg.body = json.dumps(data)

        await sensor_agent.send(msg)

        print(f"📤 Enviado para agente ({conversation_id})")

    # enviar no loop correto
    asyncio.run_coroutine_threadsafe(send(), sensor_agent_loop)

    try:
        result = future.result()  # sem timeout

        print(f"✅ Resposta recebida ({conversation_id})")
        return result

    except Exception as e:
        print(f"❌ Erro ao obter resposta: {e}")
        pending_requests.pop(conversation_id, None)
        return None


# =========================
# BEHAVIOUR PARA RECEBER RESPOSTAS
# =========================


class ResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
            print("📩 Recebi mensagem no bridge")  # 🔥 DEBUG

            conv_id = msg.get_metadata("conversation-id")
            performative = msg.get_metadata("performative")

            print(f"📩 Reply recebido ({performative}) - {conv_id}")

            if conv_id in pending_requests:
                future = pending_requests.pop(conv_id)

                if not future.done():
                    future.set_result(msg.body)


# =========================
# FUNÇÃO PARA INICIAR BRIDGE
# =========================


def start_bridge(agent, loop):
    global sensor_agent, sensor_agent_loop

    sensor_agent = agent
    sensor_agent_loop = loop

    # 🔥 Template CRÍTICO
    template = Template()
    template.set_metadata("performative", "inform")
    template.set_metadata("ontology", "sensor-data")

    agent.add_behaviour(ResponseBehaviour(), template)

    print("🔗 Bridge Flask <-> SPADE iniciada")
