Example commands

PPO export + validate + copy:
python Dance4Life/RL/export/export_onnx.py --algo ppo --model Dance4Life/RL/training/checkpoints/ppo/best/best_model --validate

DQN export + validate + copy:
python Dance4Life/RL/export/export_onnx.py --algo dqn --model Dance4Life/RL/training/checkpoints/dqn/best/best_model --validate

Export without copying to Android assets:
python Dance4Life/RL/export/export_onnx.py --algo ppo --no-copy