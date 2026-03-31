# from spade.agent import Agent
# from spade.behaviour import CyclicBehaviour
# import json

# from services.firebase_service import save_match
# from models.rl_model import RLModel


# class MatchingAgent(Agent):

#     def __init__(self, jid, password):
#         super().__init__(jid, password)
#         self.users = []
#         self.rl_models = {}  # RL por utilizador

#     def get_model(self, user_id):
#         if user_id not in self.rl_models:
#             self.rl_models[user_id] = RLModel()
#         return self.rl_models[user_id]

#     def calculate_reward(self, data):
#         hr = data.get("hr", 0)
#         atividade = data.get("atividade")

#         reward = 0

#         if atividade == "intensa":
#             reward += 1

#         if hr > 100:
#             reward += 1

#         if atividade == "parado":
#             reward -= 0.5

#         return reward

#     class ReceiveBehaviour(CyclicBehaviour):
#         async def run(self):
#             msg = await self.receive(timeout=10)

#             if msg:
#                 data = json.loads(msg.body)
#                 user_id = data["userId"]

#                 agent = self.agent
#                 model = agent.get_model(user_id)

#                 state = data.get("atividade")

#                 # 🔥 escolher ação com RL
#                 action = model.choose_action(state)

#                 print(f"[RL] Estado={state} → Ação={action}")

#                 reward = agent.calculate_reward(data)

#                 # 🔁 atualizar RL
#                 if model.last_state is not None:
#                     model.update(model.last_state, model.last_action, reward)

#                 model.last_state = state
#                 model.last_action = action

#                 # 🔥 só faz match se RL disser
#                 if action == "match":
#                     agent.users.append(data)

#                     for u in agent.users:
#                         if u["userId"] != user_id:
#                             if u["atividade"] == "parado" and data["atividade"] == "parado":

#                                 match = {
#                                     "user1": user_id,
#                                     "user2": u["userId"]
#                                 }

#                                 print(f"Match RL: {match}")

#                                 try:
#                                     save_match(match)
#                                 except Exception as e:
#                                     print("Erro Firebase:", e)

#                                 return




from agents.base_agent import BaseAgent

class MatchingAgent(BaseAgent):
    def __init__(self, interface_agent):
        super().__init__("MatchingAgent")
        self.interface = interface_agent
        self.users = []

    def handle(self, data):
        self.users.append(data)

        for u in self.users:
            if u["userId"] != data["userId"]:

                if u["atividade"] == "parado" and data["atividade"] == "parado":

                    match = {
                        "user1": data["userId"],
                        "user2": u["userId"]
                    }

                    self.interface.notify_match(match)
                    return match

        return {"status": "no_match"}