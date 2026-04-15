from trainer import Trainer
from metrics import Metrics

class RLPipeline:
    def run(self):
        trainer = Trainer()

        print("Training PPO...")
        ppo = trainer.train_ppo()

        print("Training DQN...")
        dqn = trainer.train_dqn()

        metrics = Metrics()

        ppo_r, ppo_l = metrics.evaluate(ppo)
        dqn_r, dqn_l = metrics.evaluate(dqn)

        print("\n=== RESULTS ===")
        print("PPO → reward:", ppo_r, "length:", ppo_l)
        print("DQN → reward:", dqn_r, "length:", dqn_l)