from agents.base_agent import BaseAgent
from services.firebase_service import save_raw_activity


class SensorAgent(BaseAgent):
    def __init__(self, preprocessing_agent):
        super().__init__("SensorAgent")
        self.preprocessing_agent = preprocessing_agent

    def handle(self, data):
        self.log(f"Dados recebidos: {data}")

        acc = data.get("acc")
        hr = data.get("hr")
        ritmo = data.get("ritmo")

        # IA
        actividade = calcular_atividade(acc, hr)
        interesse = calcular_interesse(acc, ritmo)

        # 🔵 dados crus
        raw_data = {
            "acc": data.get("acc", 0),
            "actividade": actividade,
            "interesse": interesse,
            "hr": data.get("hr", 0),
            "ritmo": ritmo,
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "timestamp": data.get("timestamp"),
            "userId": data.get("userId")
        }

        # guardar raw
        try:
            save_raw_activity(raw_data)
        except Exception as e:
            self.log(f"Erro ao guardar RAW: {e}")

        # enviar para pipeline
        return self.preprocessing_agent.handle(raw_data)
    

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