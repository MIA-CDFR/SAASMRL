"""
Dance4Life – ONNX export script
==================================
Extracts the trained PPO actor network and exports it as an ONNX model
ready to be bundled in the Android app.

The ONNX model accepts one input tensor:
    obs: float32 [1, 4]
        [steps_last_hour / 1000, sedentary_minutes / 480,
         energy_level / 10, mobility_confidence / 10]

The ONNX model produces one output tensor:
    action_logits: float32 [1, 4]
        argmax → action index:  0=rest  1=stretch  2=walk  3=dance

Usage:
    python export_onnx.py
    python export_onnx.py --model ../training/checkpoints/best/best_model \
                          --output dance4life_coach_v1.onnx
    python export_onnx.py --validate
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from stable_baselines3 import PPO


def export(model_path: str, output_path: str) -> None:
    print(f"[dance4life] Loading SB3 model from {model_path} …")
    sb3_model = PPO.load(model_path)

    policy = sb3_model.policy
    policy.eval()

    # SB3 MlpPolicy actor: obs → latent features → action logits
    class ActorOnly(torch.nn.Module):
        def __init__(self, p: type(policy)) -> None:
            super().__init__()
            self._policy = p

        def forward(self, obs: torch.Tensor) -> torch.Tensor:
            features = self._policy.extract_features(obs, self._policy.pi_features_extractor)
            latent_pi, _ = self._policy.mlp_extractor(features)
            return self._policy.action_net(latent_pi)

    actor = ActorOnly(policy)
    actor.eval()

    dummy_input = torch.zeros(1, 4, dtype=torch.float32)

    print(f"[dance4life] Exporting to {output_path} …")
    torch.onnx.export(
        actor,
        dummy_input,
        output_path,
        input_names=["obs"],
        output_names=["action_logits"],
        dynamic_axes={"obs": {0: "batch_size"}, "action_logits": {0: "batch_size"}},
        opset_version=17,
        do_constant_folding=True,
    )
    print(f"[dance4life] ONNX model saved → {output_path}")


def validate(onnx_path: str) -> None:
    print(f"[dance4life] Validating {onnx_path} with onnxruntime …")
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    test_cases = [
        # (steps_last_hour/1000, sedentary/480, energy/10, mobility/10)
        [0.1, 0.8, 0.3, 0.4],   # very sedentary, low energy
        [0.5, 0.2, 0.7, 0.8],   # active, good energy
        [0.0, 1.0, 0.5, 0.5],   # maximum sedentary
        [1.0, 0.0, 1.0, 1.0],   # very active, high energy
    ]

    action_names = ["rest", "stretch", "walk", "dance"]
    for obs in test_cases:
        x = np.array([obs], dtype=np.float32)
        logits = session.run(None, {input_name: x})[0][0]
        action = int(np.argmax(logits))
        steps = int(obs[0] * 1000)
        sed = int(obs[1] * 480)
        energy = int(obs[2] * 10)
        mob = int(obs[3] * 10)
        print(
            f"  steps={steps:4d}  sed={sed:3d}min  energy={energy:2d}  mob={mob:2d}"
            f"  →  [{action}] {action_names[action]}"
            f"  logits={[f'{v:.2f}' for v in logits]}"
        )

    print("[dance4life] Validation passed ✓")


def copy_to_assets(onnx_path: str, workspace_root: Path) -> None:
    dest = workspace_root / "apps/android/app/src/main/assets/models"
    dest.mkdir(parents=True, exist_ok=True)
    dest_file = dest / Path(onnx_path).name
    shutil.copy2(onnx_path, dest_file)
    print(f"[dance4life] Copied to Android assets → {dest_file}")


def main() -> None:
    here = Path(__file__).parent
    workspace_root = here.parent.parent.parent.parent  # ml/export → ml → workspace root

    default_model = str(here.parent / "training/checkpoints/best/best_model")
    default_output = str(here / "dance4life_coach_v1.onnx")

    parser = argparse.ArgumentParser(description="Export dance4life coach to ONNX")
    parser.add_argument("--model", default=default_model, help="Path to SB3 model (no .zip)")
    parser.add_argument("--output", default=default_output, help="Output ONNX file path")
    parser.add_argument("--validate", action="store_true", help="Run validation after export")
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Skip copying the ONNX file to Android assets/",
    )
    args = parser.parse_args()

    export(args.model, args.output)
    validate(args.output)

    if not args.no_copy:
        copy_to_assets(args.output, workspace_root)


if __name__ == "__main__":
    main()
