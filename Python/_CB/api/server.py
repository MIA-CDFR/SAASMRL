from flask import Flask, request, jsonify

app = Flask(__name__)

coordinator = None

@app.route("/MIA_SA_ASM_RL", methods=["POST"])
def receber_legacy():
    data = request.json
    result = coordinator.sensor.handle(data)
    return jsonify(result)