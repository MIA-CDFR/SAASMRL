from agents.base_agent import BaseAgent


class HARAgent(BaseAgent):
    def __init__(self, profiling_agent, safety_agent):
        super().__init__("HARAgent")
        self.profiling_agent = profiling_agent
        self.safety_agent = safety_agent

    def handle(self, data):
        acc = data["acc"]
        hr = data["hr"]

        intensidade = 0.7 * acc + 0.3 * hr

        if intensidade < 0.3:
            atividade = "parado"
        elif intensidade < 0.7:
            atividade = "leve"
        else:
            atividade = "intensa"

        data["atividade"] = atividade

        self.log(f"Atividade: {atividade}")

        # enviar para dois agentes
        self.safety_agent.handle(data)
        return self.profiling_agent.handle(data)