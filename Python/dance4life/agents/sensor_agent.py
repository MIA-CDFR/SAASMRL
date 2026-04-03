import json
import jsonpickle

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


# =========================
# LÓGICA DE NEGÓCIO
# =========================


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


# =========================
# AGENTE
# =========================


class SensorAgent(Agent):

    async def process_sensor_data(self, payload):
        if not payload:
            print("⚠️ Payload vazio")
            return None

        # decode
        if isinstance(payload, dict):
            data = payload
        else:
            try:
                data = json.loads(payload)
            except Exception:
                try:
                    data = jsonpickle.decode(payload)
                except Exception as e:
                    print(f"❌ Erro decode: {e}")
                    return None

        try:
            acc = float(data.get("acc", 0))
            hr = float(data.get("hr", 0))
            ritmo = float(data.get("ritmo", 0))

            lat = float(data.get("latitude", 0))
            lon = float(data.get("longitude", 0))

            user_id = data.get("userId")
            timestamp = data.get("timestamp")

        except Exception as e:
            print(f"❌ Erro dados: {e}")
            return None

        print("\n📥 Dados recebidos no SensorAgent:")
        print(data)

        # processamento
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

        print("\n📊 Resultado processado:")
        print(resultado)

        # guardar no Firebase
        try:
            from services.firebase_service import save_raw_activity

            save_raw_activity(resultado)
            print("💾 Guardado no Firebase")
        except Exception as e:
            print(f"❌ Firebase erro: {e}")
            return None

        return resultado

    # =========================
    # BEHAVIOUR
    # =========================


    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            print("👀 À espera de mensagens...")   # 👈 DEBUG

            msg = await self.receive(timeout=10)

            if msg:
                print("📨 Mensagem recebida no SensorAgent")
                print("🔍 Metadata:", msg.metadata)
                print("📦 Body:", msg.body)

                # obter conversation-id para resolver o future diretamente
                conversation_id = msg.get_metadata("conversation-id")

                result = await self.agent.process_sensor_data(msg.body)

                # resolver o future diretamente (sem XMPP reply)
                from messaging.to_sensor_agent import resolve_pending

                if result:
                    result_body = json.dumps(result)
                else:
                    result_body = json.dumps({"status": "error"})

                print(f"📤 A resolver future do SensorAgent ({conversation_id})")
                resolve_pending(conversation_id, result_body)

    # =========================
    # SETUP
    # =========================

    async def setup(self):
        print("🚀 SensorAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviour())
