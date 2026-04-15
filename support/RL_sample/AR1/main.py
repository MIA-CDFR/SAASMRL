import numpy as np
from stable_baselines3 import DQN, PPO

from custom_gym_env import CustomGymEnv

def train_dqn():
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
    return model


def train_ppo():
    env = CustomGymEnv()
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        verbose=1
    )
    model.learn(total_timesteps=50000)
    model.save("ppo_model")
    return model


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


if __name__ == "__main__":
    print("=== Training DQN ===")
    dqn_model = train_dqn()

    print("=== Training PPO ===")
    ppo_model = train_ppo()

    print("=== Evaluating Models ===")

    dqn_results = evaluate(dqn_model)
    ppo_results = evaluate(ppo_model)

    print("--- RESULTS ---")
    print("DQN:", dqn_results)
    print("PPO:", ppo_results)