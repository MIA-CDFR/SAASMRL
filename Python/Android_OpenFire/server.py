from flask import Flask, request, jsonify
import json

app = Flask(__name__)

sensor_agent = None
sensor_agent_jid = "sensor_agent@localhost"


def send_data_to_sensor_agent(data):
    if sensor_agent is None or sensor_agent.client is None:
        return False

    sensor_agent.client.send_message(
        mto=sensor_agent_jid,
        mbody=json.dumps(data),
        mtype="chat",
    )
    return True


@app.route('/MIA_SA_ASM_RL', methods=['POST'])
def receber_dados():
    data = request.json

    print("\nDados recebidos:")
    print(data)

    sent = send_data_to_sensor_agent(data)
    if not sent:
        return jsonify({"status": "agent_not_ready"}), 503

    return jsonify({"status": "ok"}), 200
