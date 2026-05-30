"""Dance4Life RL environment for coaching intensity control.

State (continuous, [0, 10]):
    - activity_level: current user movement level
    - physical_fatigue: accumulated physiological fatigue
    - irritation_level: alarm-fatigue caused by interventions

Actions (discrete, 4):
    0 - silence
    1 - low intensity coaching
    2 - medium intensity coaching
    3 - high intensity coaching

Rewards:
    +15 when state is in the healthy zone
    -5 when activity is dangerously sedentary (< 2)
    -50 and terminal game over when physical_fatigue >= 10 or irritation_level >= 10
"""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class MovementEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    STATE_LOW = 0.0
    STATE_HIGH = 10.0

    N_ACTIONS = 4
    ACTION_LABELS = [
        "silence",
        "low_intensity",
        "medium_intensity",
        "high_intensity",
    ]

    IDEAL_ACTIVITY_MIN = 4.0
    IDEAL_ACTIVITY_MAX = 7.0
    IDEAL_FATIGUE_MAX = 7.0
    IDEAL_IRRITATION_MAX = 5.0

    CRITICAL_LIMIT = 10.0

    def __init__(self, episode_length: int = 96):
        super().__init__()
        self.episode_length = episode_length

        self.observation_space = spaces.Box(
            low=np.full(3, self.STATE_LOW, dtype=np.float32),
            high=np.full(3, self.STATE_HIGH, dtype=np.float32),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self.N_ACTIONS)

        self._activity_level: float = 0.0
        self._physical_fatigue: float = 0.0
        self._irritation_level: float = 0.0
        self._current_step: int = 0

    # ------------------------------------------------------------------
    # Gymnasium API
    # ------------------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._current_step = 0

        rng = self.np_random
        self._activity_level = float(rng.uniform(2.0, 5.0))
        self._physical_fatigue = float(rng.uniform(1.0, 4.0))
        self._irritation_level = float(rng.uniform(0.0, 3.0))

        return self._obs(), {}

    def step(self, action: int):
        assert self.action_space.contains(action)

        self._update_state(action)
        self._current_step += 1

        critical_fatigue = self._physical_fatigue >= self.CRITICAL_LIMIT
        critical_irritation = self._irritation_level >= self.CRITICAL_LIMIT
        terminated = bool(critical_fatigue or critical_irritation)
        truncated = self._current_step >= self.episode_length and not terminated
        reward = self._compute_reward(terminated)

        info = {
            "game_over": terminated,
            "terminated_by": (
                "physical_fatigue"
                if critical_fatigue
                else "irritation"
                if critical_irritation
                else None
            ),
            "survived": not terminated,
        }

        return self._obs(), reward, terminated, truncated, info

    def render(self):
        print(
            f"Step {self._current_step:3d} | "
            f"Activity: {self._activity_level:4.1f}/10 | "
            f"Fatigue: {self._physical_fatigue:4.1f}/10 | "
            f"Irritation: {self._irritation_level:4.1f}/10"
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        return np.array(
            [
                self._activity_level,
                self._physical_fatigue,
                self._irritation_level,
            ],
            dtype=np.float32,
        )

    def _compute_reward(self, terminated: bool) -> float:
        if terminated:
            return -50.0

        reward = 0.0

        if (
            self.IDEAL_ACTIVITY_MIN <= self._activity_level <= self.IDEAL_ACTIVITY_MAX
            and self._physical_fatigue < self.IDEAL_FATIGUE_MAX
            and self._irritation_level < self.IDEAL_IRRITATION_MAX
        ):
            reward += 15.0

        if self._activity_level < 2.0:
            reward -= 5.0

        return float(reward)

    def _update_state(self, action: int) -> None:
        rng = self.np_random

        action_deltas = {
            0: (-0.9, -0.8, -1.0),
            1: (0.4, -0.3, 0.2),
            2: (1.2, 0.9, 0.7),
            3: (2.0, 1.9, 1.4),
        }
        activity_delta, fatigue_delta, irritation_delta = action_deltas[action]

        activity_noise = float(rng.normal(0.0, 0.25))
        fatigue_noise = float(rng.normal(0.0, 0.15))
        irritation_noise = float(rng.normal(0.0, 0.20))

        fatigue_coupling = 0.08 * max(self._activity_level - 6.0, 0.0)
        recovery_bonus = 0.10 * max(3.0 - self._activity_level, 0.0)

        self._activity_level = float(
            np.clip(
                self._activity_level + activity_delta + activity_noise,
                self.STATE_LOW,
                self.STATE_HIGH,
            )
        )
        self._physical_fatigue = float(
            np.clip(
                self._physical_fatigue
                + fatigue_delta
                + fatigue_coupling
                - recovery_bonus
                + fatigue_noise,
                self.STATE_LOW,
                self.STATE_HIGH,
            )
        )
        self._irritation_level = float(
            np.clip(
                self._irritation_level + irritation_delta - 0.10 + irritation_noise,
                self.STATE_LOW,
                self.STATE_HIGH,
            )
        )
