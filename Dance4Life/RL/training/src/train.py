"""Dance4Life training script.

Trains one or both RL policies (PPO and DQN) on the same custom environment,
so results can be compared with consistent metrics.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
)
from stable_baselines3.common.env_util import make_vec_env

# Ensure src/ is on the path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from env.movement_env import MovementEnv


SUPPORTED_ALGOS = ("ppo", "dqn")


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def make_envs(n_envs: int, episode_length: int, seed: int):
    return make_vec_env(
        lambda: MovementEnv(episode_length=episode_length),
        n_envs=n_envs,
        seed=seed,
    )


def _build_model(algo: str, algo_cfg: dict, env, seed: int, log_dir: Path):
    if algo == "ppo":
        return PPO(
            policy="MlpPolicy",
            env=env,
            learning_rate=algo_cfg["learning_rate"],
            n_steps=algo_cfg["n_steps"],
            batch_size=algo_cfg["batch_size"],
            n_epochs=algo_cfg["n_epochs"],
            gamma=algo_cfg["gamma"],
            gae_lambda=algo_cfg["gae_lambda"],
            clip_range=algo_cfg["clip_range"],
            ent_coef=algo_cfg["ent_coef"],
            vf_coef=algo_cfg["vf_coef"],
            max_grad_norm=algo_cfg["max_grad_norm"],
            tensorboard_log=str(log_dir),
            seed=seed,
            verbose=1,
        )

    if algo == "dqn":
        return DQN(
            policy="MlpPolicy",
            env=env,
            learning_rate=algo_cfg["learning_rate"],
            buffer_size=algo_cfg["buffer_size"],
            learning_starts=algo_cfg["learning_starts"],
            batch_size=algo_cfg["batch_size"],
            tau=algo_cfg["tau"],
            gamma=algo_cfg["gamma"],
            train_freq=algo_cfg["train_freq"],
            gradient_steps=algo_cfg["gradient_steps"],
            target_update_interval=algo_cfg["target_update_interval"],
            exploration_fraction=algo_cfg["exploration_fraction"],
            exploration_initial_eps=algo_cfg["exploration_initial_eps"],
            exploration_final_eps=algo_cfg["exploration_final_eps"],
            max_grad_norm=algo_cfg["max_grad_norm"],
            tensorboard_log=str(log_dir),
            seed=seed,
            verbose=1,
        )

    raise ValueError(f"Unsupported algorithm: {algo}")


def _train_one(algo: str, config: dict, timesteps: int) -> None:
    algo_cfg = config[algo]
    train_cfg = config["training"]
    out_cfg = config["output"]

    seed = train_cfg["seed"]
    episode_length = train_cfg["episode_length"]
    n_envs = train_cfg["n_envs"] if algo == "ppo" else 1

    base_model_dir = Path(out_cfg["model_dir"])
    base_log_dir = Path(out_cfg["log_dir"])
    experiment_tag = out_cfg["experiment_tag"]

    model_dir = base_model_dir / algo
    log_dir = base_log_dir / algo
    model_name = f"{experiment_tag}_{algo}"

    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"[dance4life] Training {model_name} for {timesteps:,} timesteps...")
    print(f"  n_envs={n_envs}, seed={seed}, episode_length={episode_length}")

    if algo == "ppo":
        train_env = make_envs(n_envs, episode_length, seed)
        eval_env = make_envs(1, episode_length, seed + 1)
    else:
        train_env = MovementEnv(episode_length=episode_length)
        eval_env = MovementEnv(episode_length=episode_length)

    model = _build_model(algo, algo_cfg, train_env, seed, log_dir)

    eval_freq = train_cfg["eval_freq"]
    if algo == "ppo":
        eval_freq = max(eval_freq // n_envs, 1)

    checkpoint_cb = CheckpointCallback(
        save_freq=max(eval_freq, 1),
        save_path=str(model_dir / "checkpoints"),
        name_prefix=model_name,
        verbose=1,
    )

    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir / "best"),
        log_path=str(log_dir),
        eval_freq=max(eval_freq, 1),
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


def train(config: dict, algo: str, total_timesteps: int | None = None) -> None:
    timesteps = int(total_timesteps or config["training"]["total_timesteps"])

    if algo == "both":
        algos = [a for a in config["training"].get("algorithms", SUPPORTED_ALGOS) if a in SUPPORTED_ALGOS]
    else:
        algos = [algo]

    if not algos:
        raise ValueError("No supported algorithms configured to train.")

    for selected_algo in algos:
        _train_one(selected_algo, config, timesteps)


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
    parser.add_argument(
        "--algo",
        choices=["ppo", "dqn", "both"],
        default="both",
        help="Algorithm to train",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    train(config, algo=args.algo, total_timesteps=args.timesteps)


if __name__ == "__main__":
    main()
