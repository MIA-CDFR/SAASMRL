from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

from firebase_db import save_activity

import dance4life_phyton.server as server

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
    async def process_sensor_data(self, payload):
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                print("Mensagem recebida nao esta em JSON valido:")
                print(payload)
                return False
        elif isinstance(payload, dict):
            data = payload
        else:
            print(f"Payload invalido recebido: {type(payload)}")
            return False

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

        server.add_message(data.get("userId"), {
            "type": "match",
            "user":"a",
            "score": "20"
        })


        print("\nResultado:")
        print(resultado)

        # guardar no Firebase
        try:
            print("1")
            save_activity(resultado)
            print("2")
        except Exception as e:
            print(f"Erro a guardar atividade no Firebase: {e}")
            return False

        # enviar para MatchingAgent
        msg_out = Message(to="matching_agent@localhost")
        msg_out.body = json.dumps(resultado)
        await self.send(msg_out)
        return True

    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                await self.agent.process_sensor_data(msg.body)

    async def setup(self):
        print("SensorAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviour())
