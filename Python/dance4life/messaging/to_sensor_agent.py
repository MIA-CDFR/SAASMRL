import asyncio
import json
import threading
import uuid

from spade.message import Message

sensor_agent = None
sensor_agent_loop = None

# guardar pedidos pendentes
pending_requests = {}


def resolve_pending(conversation_id, result):
    if conversation_id in pending_requests:
        event, result_holder = pending_requests.pop(conversation_id)
        result_holder["body"] = result
        event.set()


def send_data_to_sensor_agent(data):
    if sensor_agent is None or sensor_agent_loop is None:
        print("⚠️ Agente não está pronto")
        return None

    event = threading.Event()
    result_holder = {"body": None}

    conversation_id = str(uuid.uuid4())

    pending_requests[conversation_id] = (event, result_holder)

    async def send_message():
        # despiste do JID do agente para garantir que a mensagem é enviada para o agente correto
        print(f"CARLOS BERGUEIRA (conversation_id={conversation_id})")
        print(f"CARLOS BERGUEIRA (sensor_agent.jid={sensor_agent.jid})")

        msg = Message(to=str(sensor_agent.jid))
        # msg = Message(to="sensor_agent@mia.lan")
        # msg = Message(to=str(sensor_agent.jid.full))

        msg.set_metadata("conversation-id", conversation_id)
        msg.body = json.dumps(data)

        await sensor_agent.send(msg)
        print(f"📤 Mensagem enviada para SensorAgent ({conversation_id})")

    asyncio.run_coroutine_threadsafe(send_message(), sensor_agent_loop)

    answered = event.wait(timeout=15)

    if not answered:
        print("❌ Timeout aguardando resposta do agente")
        pending_requests.pop(conversation_id, None)
        return None

    print("✅ Resposta recebida via SPADE")
    return result_holder["body"]


def start_bridge(agent, loop):
    global sensor_agent, sensor_agent_loop
    sensor_agent = agent
    sensor_agent_loop = loop
    print("🔗 Bridge Flask <-> SPADE iniciada")
