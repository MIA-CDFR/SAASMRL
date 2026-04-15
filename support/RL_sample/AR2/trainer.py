from stable_baselines3 import PPO
from custom_gym_env import CustomGymEnv

class Trainer:
    def __init__(self, timesteps=20000, model_path="ppo_model"):
        self.env = CustomGymEnv()
        self.timesteps = timesteps
        self.model_path = model_path
        self.model = None

    def train(self):
        print("Training PPO model...")
        self.model = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            n_steps=1024,
            batch_size=64,
            gamma=0.99,
            verbose=1
        )
        self.model.learn(total_timesteps=self.timesteps)
        self.model.save(self.model_path)
        print(f"Model trained and saved at '{self.model_path}'!")