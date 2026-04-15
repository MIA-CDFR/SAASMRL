import numpy as np
from stable_baselines3 import DQN, PPO
from custom_gym_env import CustomGymEnv


def evaluate(model, episodes=50):
    env = CustomGymEnv()
    rewards = []
    lengths = []
    survival = 0

    for _ in range(episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0
        steps = 0

        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, _, _ = env.step(action)
            total_reward += reward
            steps += 1

        rewards.append(total_reward)
        lengths.append(steps)

        if steps > 50:
            survival += 1

    return {
        "avg_reward": np.mean(rewards),
        "avg_length": np.mean(lengths),
        "survival_rate": survival / episodes
    }


# Load models

dqn = DQN.load("dqn_model")
ppo = PPO.load("ppo_model")

print("DQN:", evaluate(dqn))
print("PPO:", evaluate(ppo))
