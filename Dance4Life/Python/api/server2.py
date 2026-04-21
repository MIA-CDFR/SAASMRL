import random

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
        data = request.json

        print("\n[collect_data_activities]: Dados recebidos:")
        print(data)

        return jsonify({"status": "ok"}), 200

@app.route('/set_movement_recommendation', methods=['POST'])
def set_movement_recommendation():
        data = request.json

        print("\n[set_movement_recommendation]: Dados recebidos:")
        print(data)

        return jsonify({"status": "ok"}), 200

   

@app.route('/get_user_match/<user_id>', methods=['GET'])
def get_user_match(user_id):
    add_invite(user_id, f"invite{random.randint(1000, 9999)}", f"group{random.randint(1000, 9999)}")  # Exemplo de convite para teste
    msgs = pending_messages.get(user_id, [])

    # limpar depois de enviar
    pending_messages[user_id] = []
    print(f"Enviar match para {user_id}: {msgs}")

    return jsonify(msgs)

@app.route('/get_environment_data/<user_id>/<latitude>/<longitude>/<cidade>', methods=['GET'])
def get_environment_data(user_id, latitude, longitude, cidade):
    data = {
        "temperatura": 25.5,
        "humidade": 68,
        "cidade": cidade,
        "latitude": latitude,
        "longitude": longitude
    }

    print(f"Enviar dados ambientais: {data}")

    return jsonify(data)

@app.route('/set_invite_status/<invite_id>/<status_id>', methods=['POST'])
def set_invite_status(invite_id, status_id):
    data = request.json
    #invite_id = data.get("inviteId")


    print(f"Invite {('aceite' if status_id else 'recusado')}: {invite_id}")

    return jsonify({"status": "ok"})



@app.route('/set_recomendation_status/<invite_id>/<status_id>', methods=['POST'])
def set_recomendation_status(invite_id, status_id):
    data = request.json
    #invite_id = data.get("inviteId")


    print(f"Recommendation {('aceite' if status_id else 'recusado')}: {invite_id}")

    return jsonify({"status": "ok"})

pending_messages = {}

def add_invite(user_id, invite_id, from_user):
    if user_id not in pending_messages:
        pending_messages[user_id] = []

    pending_messages[user_id].append({
        "type": "invite",
        "id": invite_id,
        #"user": from_user,
        "cluster": "Moderado"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=False)