from agents.base_agent import BaseAgent
from models.user_profile import UserProfile
from services.firebase_service import save_profile, save_activity


class ProfilingAgent(BaseAgent):
    def __init__(self, matching_agent):
        super().__init__("ProfilingAgent")
        self.matching_agent = matching_agent
        self.profiles = {}

    def handle(self, data):
        user_id = data["userId"]

        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id)

        profile = self.profiles[user_id]

        # estado RL
        state = f"{data['atividade']}"

        action = profile.choose_action(state)

        self.log(f"Estado: {state} | Ação: {action}")

        reward = self.calculate_reward(data)

        if profile.last_state is not None:
            profile.update_q(profile.last_state, profile.last_action, reward)

        profile.last_state = state
        profile.last_action = action

        # 🔥 interesse
        interesse = self.calculate_interest(data)

        # 🔥 dados enriquecidos
        activity_data = {
            "userId": user_id,
            "timestamp": data.get("timestamp"),

            "acc": data.get("acc"),
            "hr": data.get("hr"),
            "ritmo": data.get("ritmo"),

            "lat": data.get("lat"),
            "lon": data.get("lon"),

            "atividade": data.get("atividade"),
            "interesse": interesse,

            "rl_action": action
        }

        # guardar enriquecido
        try:
            save_activity(activity_data)
        except Exception as e:
            self.log(f"Erro ao guardar activity: {e}")

        # guardar RL
        try:
            save_profile(user_id, profile.q_table)
        except Exception as e:
            self.log(f"Erro ao guardar perfil: {e}")

        return self.matching_agent.handle(data)

    def calculate_reward(self, data):
        hr = data.get("hr", 0)
        atividade = data.get("atividade")

        reward = 0

        if atividade == "intensa":
            reward += 1

        if hr > 0.7:
            reward += 1

        if atividade == "parado":
            reward -= 0.5

        return reward

    def calculate_interest(self, data):
        acc = data.get("acc", 0)
        hr = data.get("hr", 0)

        score = acc * hr

        if score < 0.3:
            return "baixo"
        elif score < 0.7:
            return "medio"
        else:
            return "alto"