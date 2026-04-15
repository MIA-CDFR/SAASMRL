import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CustomGymEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)
        self.action_space = spaces.Discrete(4)
        self.state = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([
            np.random.uniform(0.3, 0.6),
            np.random.uniform(0.2, 0.4),
            np.random.uniform(0.1, 0.3)
        ], dtype=np.float32)
        return self.state, {}

    def step(self, action):
        atividade, fadiga, irritacao = self.state

        if action == 0:
            atividade -= np.random.uniform(0.05, 0.15)
            fadiga -= np.random.uniform(0.1, 0.2)
            irritacao -= np.random.uniform(0.1, 0.2)
        elif action == 1:
            atividade += np.random.uniform(0.05, 0.2)
            fadiga += np.random.uniform(0.05, 0.1)
            irritacao += np.random.uniform(0.02, 0.05)
        elif action == 2:
            atividade += np.random.uniform(0.2, 0.4)
            fadiga += np.random.uniform(0.2, 0.4)
            irritacao += np.random.uniform(0.1, 0.2)
        elif action == 3:
            atividade += np.random.uniform(0.4, 0.6)
            fadiga += np.random.uniform(0.4, 0.6)
            irritacao += np.random.uniform(0.2, 0.4)

        atividade = np.clip(atividade, 0, 1)
        fadiga = np.clip(fadiga, 0, 1)
        irritacao = np.clip(irritacao, 0, 1)

        self.state = np.array([atividade, fadiga, irritacao], dtype=np.float32)

        reward = (atividade - fadiga - irritacao) * 2

        if 0.4 <= atividade <= 0.7 and fadiga < 0.7 and irritacao < 0.5:
            reward += 15
        if atividade < 0.2:
            reward -= 5

        done = (fadiga >= 1.0 or irritacao >= 1.0)
        if done:
            reward -= 50

        return self.state, reward, done, False, {}