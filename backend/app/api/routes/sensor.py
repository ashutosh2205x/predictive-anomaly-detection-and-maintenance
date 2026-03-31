from fastapi import APIRouter
from app.db.mongo import collection
from app.services.ml_service import detect_anomaly, train_model, model, is_trained
from app.services.prediction_service import predict_future
from app.services.ai_service import generate_explanation
import pandas as pd
from app.utils.stats import update_stats, compute_z

RETRAIN_INTERVAL = 50

router = APIRouter()

index = 0

@router.get("/next")
def next_data():
    global index

    data = list(
        collection.find({}, {"_id": 0})
        .sort("timestamp", 1)
        .limit(200)
    )

    if not data:
        return {"error": "No data in DB"}

    df = pd.DataFrame(data)

    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["vibration"] = pd.to_numeric(df["vibration"], errors="coerce")
    df["pressure"] = pd.to_numeric(df["pressure"], errors="coerce")

    df = df.dropna()

    if index >= len(df):
        index = 0

    row = df.iloc[-1]

    if not is_trained:
        train_model(df)

    if index % RETRAIN_INTERVAL == 0:
        train_model(df)

    if index % 50 == 0:
        update_stats(df)

    z = compute_z(row["temperature"])

    pred, score = detect_anomaly(row)

    severity = "critical" if pred == -1 else "normal"

    prediction = predict_future(df, model)

    explanation = generate_explanation(row, severity, prediction)

    # Update DB record with results
    collection.update_one(
        {"timestamp": row["timestamp"]},
        {"$set": {
            "anomaly": pred,
            "score": score,
            "severity": severity,
            "prediction": prediction,
            "explanation": explanation
        }}
    )

    return {
        **row.to_dict(),
        "anomaly": pred,
        "score": score,
        "severity": severity,
        "prediction": prediction,
        "explanation": explanation
    }