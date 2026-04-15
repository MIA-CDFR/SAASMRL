from trainer import Trainer
from evaluator import Evaluator

class RLPipeline:
    def __init__(self, timesteps=20000, model_path="ppo_model"):
        self.trainer = Trainer(timesteps=timesteps, model_path=model_path)
        self.evaluator = None
        self.model_path = model_path

    def run_training(self):
        self.trainer.train()

    def run_evaluation(self):
        self.evaluator = Evaluator(model_path=self.model_path)
        self.evaluator.test_random_cases()

    def run_all(self):
        print("=== RL PIPELINE (OOP, multi-file) ===")
        self.run_training()
        self.run_evaluation()