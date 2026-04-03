import asyncio
import json
import threading

sensor_agent = None
sensor_agent_loop = None


def send_data_to_sensor_agent(data):
    if sensor_agent is None or sensor_agent_loop is None:
        print("⚠️ Agente não está pronto")
        return None

    event = threading.Event()
    result_holder = {"body": None}

    async def run_in_agent_loop():
        try:
            result = await sensor_agent.process_sensor_data(data)
            if result:
                result_holder["body"] = json.dumps(result)
            else:
                result_holder["body"] = json.dumps({"status": "error"})
        except Exception as e:
            print(f"❌ Erro no agente: {e}")
            result_holder["body"] = json.dumps({"status": "error"})
        finally:
            event.set()

    asyncio.run_coroutine_threadsafe(run_in_agent_loop(), sensor_agent_loop)

    answered = event.wait(timeout=15)

    if not answered:
        print("❌ Timeout aguardando resposta do agente")
        return None

    print("✅ Resposta recebida")
    return result_holder["body"]


def start_bridge(agent, loop):
    global sensor_agent, sensor_agent_loop
    sensor_agent = agent
    sensor_agent_loop = loop
    print("🔗 Bridge Flask <-> SPADE iniciada")
