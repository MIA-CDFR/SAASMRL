# RL Training Workspace

This folder is dedicated to experimentation and training.

## Dance4Life practical setup

This project trains a coaching agent that balances:

- activity promotion (avoid sedentary behavior)
- physical fatigue risk
- alarm-fatigue / irritation risk

Environment (`src/env/movement_env.py`):

- state: `[activity_level, physical_fatigue, irritation_level]`, each in `[0, 10]`
- actions: `0=silence`, `1=low`, `2=medium`, `3=high` coaching intensity
- rewards:
	- `+15` in healthy zone (`activity in [4,7]`, `fatigue < 7`, `irritation < 5`)
	- `-5` when `activity < 2`
	- `-50` and terminal game-over if fatigue or irritation reaches critical level (`>= 10`)

## Training

Train both algorithms (default):

```bash
python src/train.py --config config/training_config.yaml --algo both
```

Train only one algorithm:

```bash
python src/train.py --algo ppo
python src/train.py --algo dqn
```

## Evaluation and comparison

Compare PPO vs DQN with the required metrics:

- mean reward per episode
- mean episode duration
- survival rate

```bash
python src/evaluate.py --algo compare --episodes 20
```

Single-model evaluation:

```bash
python src/evaluate.py --algo ppo --model checkpoints/ppo/best/best_model
python src/evaluate.py --algo dqn --model checkpoints/dqn/best/best_model
```

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
