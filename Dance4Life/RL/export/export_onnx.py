"""Dance4Life ONNX export script.

Exports either PPO or DQN policies trained in Stable-Baselines3.
Input shape is always [batch, 3] for:
    [activity_level, physical_fatigue, irritation_level]
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from stable_baselines3 import DQN, PPO


def _load_model(algo: str, model_path: str):
    if algo == "ppo":
        return PPO.load(model_path)
    if algo == "dqn":
        return DQN.load(model_path)
    raise ValueError(f"Unsupported algorithm: {algo}")


def export(algo: str, model_path: str, output_path: str) -> None:
    print(f"[dance4life] Loading {algo.upper()} model from {model_path}...")
    sb3_model = _load_model(algo, model_path)

    policy = sb3_model.policy
    policy.eval()

    class PolicyOnly(torch.nn.Module):
        def __init__(self, p: type(policy)) -> None:
            super().__init__()
            self._policy = p

        def forward(self, obs: torch.Tensor) -> torch.Tensor:
            if algo == "ppo":
                features = self._policy.extract_features(obs, self._policy.pi_features_extractor)
                latent_pi, _ = self._policy.mlp_extractor(features)
                return self._policy.action_net(latent_pi)

            # DQN exports Q-values for each action.
            return self._policy.q_net(obs)

    model_for_export = PolicyOnly(policy)
    model_for_export.eval()

    dummy_input = torch.zeros(1, 3, dtype=torch.float32)

    print(f"[dance4life] Exporting to {output_path}...")
    torch.onnx.export(
        model_for_export,
        dummy_input,
        output_path,
        input_names=["obs"],
        output_names=["action_scores"],
        dynamic_axes={"obs": {0: "batch_size"}, "action_scores": {0: "batch_size"}},
        opset_version=17,
        do_constant_folding=True,
    )
    print(f"[dance4life] ONNX model saved → {output_path}")


def validate(onnx_path: str) -> None:
    print(f"[dance4life] Validating {onnx_path} with onnxruntime...")
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    test_cases = [
        [1.0, 2.0, 1.0],
        [5.0, 4.0, 3.0],
        [7.0, 8.0, 6.0],
        [2.0, 9.0, 9.0],
    ]

    action_names = ["silence", "low", "medium", "high"]
    for obs in test_cases:
        x = np.array([obs], dtype=np.float32)
        scores = session.run(None, {input_name: x})[0][0]
        action = int(np.argmax(scores))
        activity = obs[0]
        fatigue = obs[1]
        irritation = obs[2]
        print(
            f"  activity={activity:4.1f}  fatigue={fatigue:4.1f}  irritation={irritation:4.1f}"
            f"  →  [{action}] {action_names[action]}"
            f"  scores={[f'{v:.2f}' for v in scores]}"
        )

    print("[dance4life] Validation passed ✓")


def copy_to_assets(onnx_path: str, workspace_root: Path) -> None:
    dest = workspace_root / "AndroidSensor/app/src/main/assets/models"
    dest.mkdir(parents=True, exist_ok=True)
    dest_file = dest / Path(onnx_path).name
    shutil.copy2(onnx_path, dest_file)
    print(f"[dance4life] Copied to Android assets → {dest_file}")


def main() -> None:
    here = Path(__file__).parent
    workspace_root = here.parent.parent.parent.parent  # RL/export -> Dance4Life root

    default_model = str(here.parent / "training/checkpoints/ppo/best/best_model")
    default_output = str(here / "dance4life_coach_v2_ppo.onnx")

    parser = argparse.ArgumentParser(description="Export dance4life coach to ONNX")
    parser.add_argument(
        "--algo",
        choices=["ppo", "dqn"],
        default="ppo",
        help="Algorithm used by the SB3 model",
    )
    parser.add_argument("--model", default=default_model, help="Path to SB3 model (no .zip)")
    parser.add_argument("--output", default=default_output, help="Output ONNX file path")
    parser.add_argument("--validate", action="store_true", help="Run validation after export")
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Skip copying the ONNX file to Android assets/",
    )
    args = parser.parse_args()

    if args.algo == "dqn" and args.output == default_output:
        args.output = str(here / "dance4life_coach_v2_dqn.onnx")

    export(args.algo, args.model, args.output)
    if args.validate:
        validate(args.output)

    if not args.no_copy:
        copy_to_assets(args.output, workspace_root)


if __name__ == "__main__":
    main()
