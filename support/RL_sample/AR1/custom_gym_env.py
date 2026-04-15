import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CustomGymEnv(gym.Env):
    def __init__(self):
        super(CustomGymEnv, self).__init__()

        # State: [atividade, fadiga, irritacao]
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)

        # Actions: 0,1,2,3
        self.action_space = spaces.Discrete(4)

        self.state = None
        self.last_action = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([
            np.random.uniform(0.3, 0.6),  # atividade
            np.random.uniform(0.2, 0.4),  # fadiga
            np.random.uniform(0.1, 0.3)   # irritacao
        ], dtype=np.float32)
        self.last_action = None
        return self.state, {}

    def step(self, action):
        atividade, fadiga, irritacao = self.state

        # Dinâmica
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

        # Clip
        atividade = np.clip(atividade, 0, 1)
        fadiga = np.clip(fadiga, 0, 1)
        irritacao = np.clip(irritacao, 0, 1)

        self.state = np.array([atividade, fadiga, irritacao], dtype=np.float32)

        # Reward
        reward = 0

        # Zona ideal (normalizada ~ equivalente a [4-7])
        if 0.4 <= atividade <= 0.7 and fadiga < 0.7 and irritacao < 0.5:
            reward += 15

        # Sedentarismo
        if atividade < 0.2:
            reward -= 5

        # Reward shaping
        reward += (atividade - fadiga - irritacao) * 2

        # Penalizar repetição
        if self.last_action == action:
            reward -= 1

        self.last_action = action

        # Terminação
        # Terminação
        done = (fadiga >= 1.0 or irritacao >= 1.0)
        if done:
            reward -= 50

        return self.state, reward, done, False, {}