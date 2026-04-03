from flask import Flask, request, jsonify
import json

from messaging.to_sensor_agent import send_data_to_sensor_agent

app = Flask(__name__)


@app.route("/collect_data_activities", methods=["POST"])
def collect_data_activities():
    data = request.json

    print("\n📥 Dados recebidos no Flask:")
    print(data)

    # 🔗 Enviar via SPADE (CORRETO)
    response = send_data_to_sensor_agent(data)

    if response is None:
        return jsonify({"status": "timeout"}), 504

    try:
        return jsonify(json.loads(response)), 200
    except Exception:
        return jsonify({"raw_response": response}), 200
