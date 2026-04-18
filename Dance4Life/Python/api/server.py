from flask import Flask, request, jsonify
import asyncio

from agents.base_sender_agent import BaseSenderAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives

app = Flask(__name__)


sender_agent = BaseSenderAgent(
    AgentAddresses.API_AGENT,
    AGENT_PASSWORD
)

def start_api():
    sender_agent.start_background()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


def stop_api():
    sender_agent.stop_background()



@app.route('/collect_data_activities', methods=['POST'])
def collect_data_activities():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "details": "Body JSON inválido ou vazio"
            }), 400

        print("\nDados recebidos:")
        print(data)

        future = asyncio.run_coroutine_threadsafe(
            sender_agent.send_message(
                payload=data,
                agent_to=AgentAddresses.SENSOR_AGENT,
                performative=AgentPerformatives.REQUEST,
                ontology=AgentOntologies.SENSOR_ACTIVITY
            ),
            sender_agent.agent_loop
        )

        future.result()

        return jsonify({
            "status": "ok",
            "message": "Dados enviados para o Sensor Agent"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        sender_agent.stop_background()

# import random

# from flask import Flask, request, jsonify
# import asyncio
# from pydantic import ValidationError
# #from agents.api_agent import ApiAgent
# from model.data_model import SensorActivityData

# from spade.agent import Agent
# from spade.message import Message
# import jsonpickle


# app = Flask(__name__)

# def init_agent(agent, loop):
#     print("ApiAgent e sensor_loop inicializados")


# class APISenderAgent(Agent):
#     async def send_sensor_data(self, payload: dict, agent_to, performative, ontology):
#         msg = Message(to=agent_to)
#         msg.set_metadata("performative", performative)
#         msg.set_metadata("ontology", ontology)
#         msg.body = jsonpickle.encode(payload)

#         await self.send(msg)
#         print(f"Mensagem enviada: {payload}")


# spade_agent = APISenderAgent("api_agent@localhost", "password")


# @app.on_event("startup")
# async def startup():
#     print("Iniciar ApiAgent...")
#     await spade_agent.start()


# @app.on_event("shutdown")
# async def shutdown():
#     print("Parar ApiAgent...")
#     await spade_agent.stop()
    
# @app.route('/collect_data_activities', methods=['POST'])
# async def collect_data_activities():
#     try:
#         data = request.json
#         #SensorActivityData

#         print("\nDados recebidos:")
#         print(data)

#         await spade_agent.send_sensor_data(data.dict(), agent_to="sensor_agent@localhost", performative="inform", ontology="sensor_activity")
#         #sensor_data = SensorActivityData(**data)
#         #print(sensor_data)
        
#         # sent = send_data_to_sensor_agent(sensor_data)
        
#         # if not sent:
#         #     return jsonify({"status": "agent_not_ready"}), 503

#         return jsonify({"status": "ok"}), 200

#     except ValidationError as e:
#         return jsonify({
#             "status": "error",
#             "details": e.errors()
#         }), 400


# @app.route('/get_updates/<user_id>', methods=['GET'])
# def get_updates(user_id):


# @app.route('/accept_invite', methods=['POST'])
# def accept_invite():