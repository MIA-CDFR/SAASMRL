# RL Training Workspace

This folder is dedicated to experimentation and training.

## Suggested internal structure

- `src/`: trainers, env wrappers, evaluation scripts
- `config/`: hyperparameters and experiment config files
- `notebooks/`: exploratory notebooks only

## Suggested baseline stack

- `gymnasium`
- `stable-baselines3`
- `numpy`
- `torch`

## Reproducibility checklist

- Set random seeds for all libraries.
- Save training config with each model artifact.
- Log metrics and evaluation episodes.
- Version exported models with semantic tags (for example `policy-v1.2.0`).
