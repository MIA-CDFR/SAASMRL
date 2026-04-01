import jsonpickle

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from services.firebase_service import save_raw_activity


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
        if not payload:
            print("Payload vazio")
            return False

        if isinstance(payload, dict):
            data = payload
        else:
            # Accept JSON or jsonpickle-encoded payload.
            try:
                data = jsonpickle.decode(payload)
            except Exception as e:
                print(f"Erro decode: {e}")
                return False

        if not isinstance(data, dict):
            print(f"Tipo invalido: {type(data)}")
            return False

        try:
            acc = float(data.get("acc", 0))
            hr = float(data.get("hr", 0))
            ritmo = float(data.get("ritmo", 0))

            lat = float(data.get("latitude", 0))
            lon = float(data.get("longitude", 0))

            user_id = data.get("userId")
            timestamp = data.get("timestamp")

        except Exception as e:
            print(f"Erro dados: {e}")
            return False

        print("\nDados recebidos:")
        print(data)

        atividade = calcular_atividade(acc, hr)
        interesse = calcular_interesse(acc, ritmo)

        resultado = {
            "userId": user_id,
            "atividade": atividade,
            "interesse": interesse,
            "acc": acc,
            "hr": hr,
            "ritmo": ritmo,
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp,
        }

        print("\nResultado:")
        print(resultado)

        try:
            save_raw_activity(resultado)
            print("Guardado no Firebase")
        except Exception as e:
            print(f"Firebase erro: {e}")
            return False

        return resultado

    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                print("Mensagem recebida")

                result = await self.agent.process_sensor_data(msg.body)

                reply = msg.make_reply()

                if result:
                    reply.set_metadata("performative", "inform")
                    reply.body = jsonpickle.encode(result)
                else:
                    reply.set_metadata("performative", "failure")
                    reply.body = jsonpickle.encode({"status": "error"})

                await self.send(reply)

    async def setup(self):
        print("SensorAgent iniciado")

        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("ontology", "sensor-data")

        self.add_behaviour(self.ReceiveBehaviour(), template)
