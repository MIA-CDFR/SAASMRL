from stable_baselines3 import DQN
from custom_gym_env import CustomGymEnv

env = CustomGymEnv()

model = DQN(
    "MlpPolicy",
    env,
    learning_rate=1e-3,
    buffer_size=100000,
    learning_starts=1000,
    batch_size=64,
    gamma=0.99,
    verbose=1
)

model.learn(total_timesteps=50000)
model.save("dqn_model")
