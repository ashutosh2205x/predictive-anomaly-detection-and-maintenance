import csv
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.db.mongo import data_collection 
import pandas as pd

router = APIRouter()


def coerce_row(row):
    numeric_fields = {
        "temperature": float,
        "pressure": float,
        "vibration": float,
        "humidity": float,
        "flow_rate": float,
        "voltage": float,
        "current": float,
        "rpm": float,
    }

    result = {"timestamp": row.get("timestamp")}

    for key, caster in numeric_fields.items():
        value = row.get(key)
        try:
            result[key] = caster(value) if value not in (None, "") else None
        except:
            result[key] = None

    result["anomaly"] = int(row["anomaly"]) if row.get("anomaly") else None

    return result


@router.get("/history")
def get_history():
    csv_path = Path(__file__).resolve().parents[3] / "sensor_data.csv"

    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        if rows:
            print("📁 Using CSV data source")
            return [coerce_row(row) for row in rows[-200:]]

    print("🗄️ Falling back to MongoDB")

    data = list(
        data_collection.find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(200)
    )

    if not data:
        raise HTTPException(status_code=404, detail="No data found in CSV or DB")

    df = pd.DataFrame(data)

    # Ensure numeric conversion
    for col in ["temperature", "pressure", "vibration"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["temperature", "pressure", "vibration"])

    return df[::-1].to_dict(orient="records")  # chronological order
