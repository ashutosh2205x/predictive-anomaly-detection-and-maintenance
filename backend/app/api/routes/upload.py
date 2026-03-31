from fastapi import APIRouter, UploadFile, File
import pandas as pd
import io
from app.db.mongo import collection  # IMPORTANT

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Ensure timestamp exists
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    records = df.to_dict(orient="records")

    if records:
        collection.insert_many(records)

    return {
        "message": "CSV uploaded and stored in MongoDB",
        "rows": len(records)
    }