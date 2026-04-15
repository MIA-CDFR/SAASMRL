"""
Dance4Life – evaluation script
================================
Loads a trained model and runs rollout episodes, printing metrics.

Usage:
    python src/evaluate.py --model checkpoints/best/best_model
    python src/evaluate.py --model checkpoints/dance4life_coach_v1_final --episodes 20 --render
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

sys.path.insert(0, str(Path(__file__).parent))

from env.movement_env import MovementEnv

ACTION_LABELS = {
    0: "rest        ",
    1: "stretch 2min",
    2: "walk    5min",
    3: "dance  10min",
}


def evaluate(model_path: str, n_episodes: int, render: bool) -> None:
    print(f"[dance4life] Loading model from {model_path} …")
    model = PPO.load(model_path)

    env = MovementEnv()
    episode_rewards: list[float] = []
    action_counts: Counter = Counter()

    for ep in range(n_episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            action = int(action)
            obs, reward, terminated, truncated, _ = env.step(action)
            total_reward += float(reward)
            action_counts[action] += 1
            done = terminated or truncated

            if render:
                _render_step(env, action, float(reward))

        episode_rewards.append(total_reward)
        if not render:
            print(f"  Episode {ep + 1:3d}: reward = {total_reward:.2f}")

    env.close()

    print("\n── Summary ──────────────────────────────────────")
    print(f"  Episodes      : {n_episodes}")
    print(f"  Mean reward   : {np.mean(episode_rewards):.2f}")
    print(f"  Std  reward   : {np.std(episode_rewards):.2f}")
    print(f"  Min / Max     : {np.min(episode_rewards):.2f} / {np.max(episode_rewards):.2f}")
    print()

    total_actions = sum(action_counts.values())
    print("  Action distribution:")
    for action_id, label in ACTION_LABELS.items():
        count = action_counts[action_id]
        pct = 100 * count / max(total_actions, 1)
        bar = "█" * int(pct / 2)
        print(f"    [{action_id}] {label}  {pct:5.1f}%  {bar}")


def _render_step(env: MovementEnv, action: int, reward: float) -> None:
    obs = env._obs()  # type: ignore[attr-defined]
    step = env._current_step  # type: ignore[attr-defined]
    steps = int(obs[0] * 1000)
    sedentary = int(obs[1] * 480)
    energy = int(obs[2] * 10)
    mobility = int(obs[3] * 10)
    label = ACTION_LABELS[action]
    print(
        f"  t={step:2d}  steps={steps:4d}  sed={sedentary:3d}min  "
        f"energy={energy:2d}  mob={mobility:2d}  "
        f"→ [{action}]{label}  r={reward:+.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate dance4life RL coach")
    parser.add_argument(
        "--model",
        default="checkpoints/best/best_model",
        help="Path to saved model (without .zip)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=10,
        help="Number of evaluation episodes",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Print step-by-step rendering",
    )
    args = parser.parse_args()

    evaluate(args.model, args.episodes, args.render)


if __name__ == "__main__":
    main()
