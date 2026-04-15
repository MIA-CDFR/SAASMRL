import numpy as np
from custom_gym_env import CustomGymEnv

class Metrics:
    def evaluate(self, model, episodes=30):
        env = CustomGymEnv()
        rewards, lengths = [], []

        for _ in range(episodes):
            obs, _ = env.reset()
            done = False
            total = 0
            steps = 0

            while not done:
                action, _ = model.predict(obs)
                obs, reward, done, _, _ = env.step(action)
                total += reward
                steps += 1

            rewards.append(total)
            lengths.append(steps)

        return np.mean(rewards), np.mean(lengths)