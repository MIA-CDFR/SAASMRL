from agents.base_agent import BaseAgent


class PreprocessingAgent(BaseAgent):
    def __init__(self, har_agent):
        super().__init__("PreprocessingAgent")
        self.har_agent = har_agent

    def handle(self, data):
        self.log("A normalizar dados")

        data["acc"] = min(data["acc"], 1)
        data["hr"] = data["hr"] / 200

        return self.har_agent.handle(data)