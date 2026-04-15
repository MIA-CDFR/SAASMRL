import numpy as np
from stable_baselines3 import PPO

class Evaluator:
    def __init__(self, model_path="ppo_model"):
        self.model_path = model_path
        self.model = PPO.load(self.model_path)

    def test_random_cases(self, n_cases=10):
        print("\n=== TESTING RANDOM CASES ===")
        for i in range(n_cases):
            estado = np.array([
                np.random.uniform(0, 1),
                np.random.uniform(0, 1),
                np.random.uniform(0, 1)
            ], dtype=np.float32)
            action, _ = self.model.predict(estado)
            print(f"Case {i+1}:")
            print(f"  State → Activity={estado[0]:.2f}, Fatigue={estado[1]:.2f}, Irritation={estado[2]:.2f}")
            print(f"  Action → {action}\n")
