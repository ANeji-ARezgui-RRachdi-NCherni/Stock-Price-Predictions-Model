import os
import joblib
import numpy as np
import json

def init():
    global model, scaler
    model_dir = os.getenv("AZUREML_MODEL_DIR")
    model = joblib.load(os.path.join(model_dir, "model.pkl"))
    scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))


def run(request_body: str) -> dict:
    # Expect JSON: {"data": [[...], ...]}
    payload = json.loads(request_body)
    raw = np.array(payload["data"])

    scaled = scaler.transform(raw)

    preds = model.predict(scaled)

    return {"predictions": preds.tolist()}