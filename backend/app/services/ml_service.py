import numpy as np
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.08)

is_trained = False


def train_model(df):
    global is_trained

    if len(df) < 20:
        return

    X = df[["temperature", "vibration", "pressure"]]

    model.fit(X)
    is_trained = True


def detect_anomaly(row):
    if not is_trained:
        return 1, 0.0

    X = [[row["temperature"], row["vibration"], row["pressure"]]]

    pred = model.predict(X)[0]
    score = model.decision_function(X)[0]

    return int(pred), float(score)