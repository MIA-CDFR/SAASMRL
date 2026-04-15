from fastapi import FastAPI
from stable_baselines3 import PPO
import numpy as np

app = FastAPI()
model = PPO.load("ppo_model")

@app.get("/predict")
def predict(a: float, f: float, i: float):
    state = np.array([a, f, i], dtype=np.float32)
    action, _ = model.predict(state)
    return {"action": int(action)}
