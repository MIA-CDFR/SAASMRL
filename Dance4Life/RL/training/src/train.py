"""
Dance4Life – PPO training script
=================================
Trains a movement coach policy using Proximal Policy Optimisation.

Usage:
    python src/train.py
    python src/train.py --config config/training_config.yaml
    python src/train.py --timesteps 1000000
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
)
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecEnv

# Ensure src/ is on the path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from env.movement_env import MovementEnv


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def make_envs(n_envs: int, episode_length: int, seed: int) -> VecEnv:
    return make_vec_env(
        lambda: MovementEnv(episode_length=episode_length),
        n_envs=n_envs,
        seed=seed,
    )


def train(config: dict, total_timesteps: int | None = None) -> None:
    ppo_cfg = config["ppo"]
    train_cfg = config["training"]
    out_cfg = config["output"]

    seed = train_cfg["seed"]
    n_envs = train_cfg["n_envs"]
    episode_length = train_cfg["episode_length"]
    timesteps = total_timesteps or train_cfg["total_timesteps"]

    model_dir = Path(out_cfg["model_dir"])
    log_dir = Path(out_cfg["log_dir"])
    model_name = out_cfg["model_name"]

    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"[dance4life] Training {model_name} for {timesteps:,} timesteps …")
    print(f"  n_envs={n_envs}, seed={seed}, episode_length={episode_length}")

    train_env = make_envs(n_envs, episode_length, seed)
    eval_env = make_envs(1, episode_length, seed + 1)

    model = PPO(
        policy="MlpPolicy",
        env=train_env,
        learning_rate=ppo_cfg["learning_rate"],
        n_steps=ppo_cfg["n_steps"],
        batch_size=ppo_cfg["batch_size"],
        n_epochs=ppo_cfg["n_epochs"],
        gamma=ppo_cfg["gamma"],
        gae_lambda=ppo_cfg["gae_lambda"],
        clip_range=ppo_cfg["clip_range"],
        ent_coef=ppo_cfg["ent_coef"],
        vf_coef=ppo_cfg["vf_coef"],
        max_grad_norm=ppo_cfg["max_grad_norm"],
        tensorboard_log=str(log_dir),
        seed=seed,
        verbose=1,
    )

    checkpoint_cb = CheckpointCallback(
        save_freq=max(train_cfg["eval_freq"] // n_envs, 1),
        save_path=str(model_dir),
        name_prefix=model_name,
        verbose=1,
    )

    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir / "best"),
        log_path=str(log_dir),
        eval_freq=max(train_cfg["eval_freq"] // n_envs, 1),
        n_eval_episodes=train_cfg["n_eval_episodes"],
        deterministic=True,
        verbose=1,
    )

    model.learn(
        total_timesteps=timesteps,
        callback=[checkpoint_cb, eval_cb],
        progress_bar=True,
    )

    final_path = model_dir / f"{model_name}_final"
    model.save(str(final_path))
    print(f"[dance4life] Saved final model to {final_path}.zip")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train dance4life RL coach")
    parser.add_argument(
        "--config",
        default="config/training_config.yaml",
        help="Path to training config YAML",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=None,
        help="Override total timesteps from config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    train(config, total_timesteps=args.timesteps)


if __name__ == "__main__":
    main()
