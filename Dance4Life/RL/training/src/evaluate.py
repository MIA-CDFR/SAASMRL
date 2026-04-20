"""Dance4Life model evaluation and PPO vs DQN comparison."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from stable_baselines3 import DQN, PPO

sys.path.insert(0, str(Path(__file__).parent))

from env.movement_env import MovementEnv

ACTION_LABELS = {
    0: "silence         ",
    1: "low intensity   ",
    2: "medium intensity",
    3: "high intensity  ",
}


def _load_model(algo: str, model_path: str):
    if algo == "ppo":
        return PPO.load(model_path)
    if algo == "dqn":
        return DQN.load(model_path)
    raise ValueError(f"Unsupported algorithm: {algo}")


def evaluate(algo: str, model_path: str, n_episodes: int, render: bool) -> dict[str, Any]:
    print(f"[dance4life] Loading {algo.upper()} model from {model_path}...")
    model = _load_model(algo, model_path)

    env = MovementEnv()
    episode_rewards: list[float] = []
    episode_lengths: list[int] = []
    survived_episodes: int = 0
    action_counts: Counter = Counter()

    for ep in range(n_episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        steps = 0
        done = False
        survived = True

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            action = int(action)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += float(reward)
            action_counts[action] += 1
            steps += 1
            done = terminated or truncated

            if terminated and info.get("game_over", False):
                survived = False

            if render:
                _render_step(env, action, float(reward))

        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        if survived:
            survived_episodes += 1

        if not render:
            status = "survived" if survived else "game-over"
            print(
                f"  Episode {ep + 1:3d}: reward={total_reward:7.2f} "
                f"steps={steps:3d} status={status}"
            )

    env.close()

    total_actions = sum(action_counts.values())
    survival_rate = survived_episodes / max(n_episodes, 1)

    summary = {
        "algo": algo,
        "episodes": n_episodes,
        "mean_reward": float(np.mean(episode_rewards)),
        "std_reward": float(np.std(episode_rewards)),
        "min_reward": float(np.min(episode_rewards)),
        "max_reward": float(np.max(episode_rewards)),
        "mean_episode_length": float(np.mean(episode_lengths)),
        "survival_rate": float(survival_rate),
        "action_counts": action_counts,
        "total_actions": total_actions,
    }

    _print_summary(summary)

    return summary


def _print_summary(summary: dict[str, Any]) -> None:
    print("\n-- Summary ---------------------------------------")
    print(f"  Algorithm     : {summary['algo'].upper()}")
    print(f"  Episodes      : {summary['episodes']}")
    print(f"  Mean reward   : {summary['mean_reward']:.2f}")
    print(f"  Std reward    : {summary['std_reward']:.2f}")
    print(f"  Min / Max     : {summary['min_reward']:.2f} / {summary['max_reward']:.2f}")
    print(f"  Mean duration : {summary['mean_episode_length']:.2f} steps")
    print(f"  Survival rate : {100 * summary['survival_rate']:.1f}%")
    print()

    print("  Action distribution:")
    for action_id, label in ACTION_LABELS.items():
        count = summary["action_counts"][action_id]
        pct = 100 * count / max(summary["total_actions"], 1)
        bar = "█" * int(pct / 2)
        print(f"    [{action_id}] {label}  {pct:5.1f}%  {bar}")


def _render_step(env: MovementEnv, action: int, reward: float) -> None:
    obs = env._obs()  # type: ignore[attr-defined]
    step = env._current_step  # type: ignore[attr-defined]
    activity = obs[0]
    fatigue = obs[1]
    irritation = obs[2]
    label = ACTION_LABELS[action]
    print(
        f"  t={step:2d}  activity={activity:4.1f}  fatigue={fatigue:4.1f}  "
        f"irritation={irritation:4.1f}  "
        f"→ [{action}]{label}  r={reward:+.2f}"
    )


def compare_models(
    ppo_model_path: str,
    dqn_model_path: str,
    n_episodes: int,
    render: bool,
) -> None:
    ppo_summary = evaluate("ppo", ppo_model_path, n_episodes, render)
    print()
    dqn_summary = evaluate("dqn", dqn_model_path, n_episodes, render)

    print("\n== PPO vs DQN comparison ========================")
    print(
        "  Mean reward      | "
        f"PPO: {ppo_summary['mean_reward']:8.2f} | "
        f"DQN: {dqn_summary['mean_reward']:8.2f}"
    )
    print(
        "  Mean duration    | "
        f"PPO: {ppo_summary['mean_episode_length']:8.2f} | "
        f"DQN: {dqn_summary['mean_episode_length']:8.2f}"
    )
    print(
        "  Survival rate    | "
        f"PPO: {100 * ppo_summary['survival_rate']:7.2f}% | "
        f"DQN: {100 * dqn_summary['survival_rate']:7.2f}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate dance4life RL coach")
    parser.add_argument(
        "--algo",
        choices=["ppo", "dqn", "compare"],
        default="compare",
        help="Evaluate one algorithm or compare both",
    )
    parser.add_argument(
        "--model",
        default="checkpoints/ppo/best/best_model",
        help="Path to saved model (without .zip)",
    )
    parser.add_argument(
        "--ppo-model",
        default="checkpoints/ppo/best/best_model",
        help="Path to PPO model when using --algo compare",
    )
    parser.add_argument(
        "--dqn-model",
        default="checkpoints/dqn/best/best_model",
        help="Path to DQN model when using --algo compare",
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

    if args.algo == "compare":
        compare_models(args.ppo_model, args.dqn_model, args.episodes, args.render)
    else:
        evaluate(args.algo, args.model, args.episodes, args.render)


if __name__ == "__main__":
    main()
