# from spade.agent import Agent
# from spade.behaviour import CyclicBehaviour
# import json

# class SensorAgent(Agent):

#     class ReceiveBehaviour(CyclicBehaviour):
#         async def run(self):
#             msg = await self.receive(timeout=10)
#             if msg:
#                 print("\nAgente recebeu:")
#                 print(msg.body)

#                 data = json.loads(msg.body)

#                 print("\nDados estruturados:")
#                 print(data)

#                 ritmo = data.get("ritmo")
#                 acc = data.get("acc")
#                 gyro = data.get("gyro")
#                 hr = data.get("hr")

#                 print(f"Ritmo: {ritmo}, HR: {hr}")

#     async def setup(self):
#         print("Agente Sensorial iniciado")
#         self.add_behaviour(self.ReceiveBehaviour())

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

from firebase_db import save_activity


def calcular_atividade(acc, hr):
    intensidade = 0.7 * acc + 0.3 * (hr / 100)

    if intensidade < 0.3:
        return "parado"
    elif intensidade < 0.8:
        return "leve"
    else:
        return "intensa"


def calcular_interesse(acc, ritmo):
    score = acc * ritmo

    if score < 0.3:
        return "baixo"
    elif score < 0.8:
        return "medio"
    else:
        return "alto"


class SensorAgent(Agent):

    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                try:
                    data = json.loads(msg.body)
                except json.JSONDecodeError:
                    print("Mensagem recebida nao esta em JSON valido:")
                    print(msg.body)
                    return

                acc = data.get("acc", 0)
                hr = data.get("hr", 0)
                ritmo = data.get("ritmo", 0)

                lat = data.get("latitude", 0)
                lon = data.get("longitude", 0)

                # IA
                atividade = calcular_atividade(acc, hr)
                interesse = calcular_interesse(acc, ritmo)

                resultado = {
                    "userId": data.get("userId"),
                    "atividade": atividade,
                    "interesse": interesse,
                    "acc": acc,
                    "hr": hr,
                    "ritmo": ritmo,
                    "lat": lat,
                    "lon": lon,
                    "timestamp": data.get("timestamp")
                }

                print("\nResultado:")
                print(resultado)

                # guardar no Firebase
                try:
                    save_activity(resultado)
                except Exception as e:
                    print(f"Erro a guardar atividade no Firebase: {e}")
                    return

                # enviar para MatchingAgent
                msg_out = Message(to="matching_agent@localhost")
                msg_out.body = json.dumps(resultado)

                await self.send(msg_out)

    async def setup(self):
        print("SensorAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviour())
