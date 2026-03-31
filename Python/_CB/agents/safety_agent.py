from agents.base_agent import BaseAgent


class SafetyAgent(BaseAgent):
    def __init__(self, interface_agent):
        super().__init__("SafetyAgent")
        self.interface_agent = interface_agent
        self.history = {}

    def handle(self, data):
        user_id = data["userId"]
        hr = data["hr"]

        if user_id not in self.history:
            self.history[user_id] = []

        self.history[user_id].append(hr)

        # alerta direto
        if hr > 0.9:
            self.interface_agent.notify_alert(user_id, "HR muito elevado!")

        # previsão simples
        if len(self.history[user_id]) > 2:
            trend = self.history[user_id][-1] - self.history[user_id][-2]

            if hr + trend > 0.85:
                self.interface_agent.notify_alert(user_id, "Risco de esforço elevado!")