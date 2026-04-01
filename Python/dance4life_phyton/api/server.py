from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

sensor_agent = None
sensor_agent_loop = None


def send_data_to_sensor_agent(data):
    if sensor_agent is None or sensor_agent_loop is None:
        return False

    try:
        future = asyncio.run_coroutine_threadsafe(
            sensor_agent.process_sensor_data(data),
            sensor_agent_loop,
        )
        return future.result(timeout=10)
    except Exception as e:
        print(f"Erro ao enviar dados para SensorAgent: {e}")
        return False


@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    data = request.json

    print("\nDados recebidos:")
    print(data)

    sent = send_data_to_sensor_agent(data)
    if not sent:
        return jsonify({"status": "agent_not_ready"}), 503

    return jsonify({"status": "ok"}), 200
