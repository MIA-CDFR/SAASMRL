from pipeline import RLPipeline

if __name__ == "__main__":
    pipeline = RLPipeline(timesteps=20000, model_path="ppo_model")
    pipeline.run_all()
