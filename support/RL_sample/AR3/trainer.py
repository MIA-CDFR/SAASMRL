from stable_baselines3 import PPO, DQN
from custom_gym_env import CustomGymEnv

class Trainer:
    def __init__(self, timesteps=20000):
        self.env = CustomGymEnv()
        self.timesteps = timesteps

    def train_ppo(self):
        model = PPO("MlpPolicy", self.env, verbose=0)
        model.learn(total_timesteps=self.timesteps)
        model.save("ppo_model")
        return model

    def train_dqn(self):
        model = DQN("MlpPolicy", self.env, verbose=0)
        model.learn(total_timesteps=self.timesteps)
        model.save("dqn_model")
        return model