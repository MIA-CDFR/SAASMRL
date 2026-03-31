from agents.base_agent import BaseAgent


class InterfaceAgent(BaseAgent):
    def __init__(self):
        super().__init__("InterfaceAgent")

    def notify_match(self, match):
        self.log(f"Notificar match: {match}")

    def notify_alert(self, user_id, message):
        self.log(f"ALERTA para {user_id}: {message}")