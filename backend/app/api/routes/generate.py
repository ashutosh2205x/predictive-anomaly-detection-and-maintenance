import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()

CSV_NAME = "sensor_data.csv"
ANOMALY_CSV_NAME = "anomaly_data.csv"


def _clamp(value, low, high):
    return max(low, min(high, value))


def _write_csv(csv_path: Path, rows_out: list[dict]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)


def _synth_rows(
    *,
    rows: int,
    interval_seconds: int,
    anomaly_rate: float,
    seed: Optional[int],
) -> list[dict]:
    rng = random.Random(seed) if seed is not None else random

    start_time = datetime.now(timezone.utc) - timedelta(seconds=interval_seconds * (rows - 1))
    rows_out = []

    for i in range(rows):
        ts = start_time + timedelta(seconds=i * interval_seconds)

        temp = 72 + 4 * math.sin(i / 60) + rng.gauss(0, 0.3)
        pressure = 101 + 2 * math.sin(i / 80) + rng.gauss(0, 0.2)
        vibration = 0.35 + 0.05 * math.sin(i / 30) + rng.gauss(0, 0.01)
        humidity = 45 + 5 * math.sin(i / 90) + rng.gauss(0, 0.5)
        flow_rate = 22 + 1.5 * math.sin(i / 70) + rng.gauss(0, 0.2)
        voltage = 230 + 1.5 * math.sin(i / 100) + rng.gauss(0, 0.3)
        current = 7.5 + 0.6 * math.sin(i / 65) + rng.gauss(0, 0.1)
        rpm = 1500 + 60 * math.sin(i / 50) + rng.gauss(0, 5)

        anomaly = 0
        if rng.random() < anomaly_rate:
            anomaly = 1
            temp += rng.uniform(6, 15)
            pressure += rng.uniform(5, 15)
            vibration += rng.uniform(0.4, 1.2)
            flow_rate -= rng.uniform(3, 7)
            voltage -= rng.uniform(10, 25)
            current += rng.uniform(2, 5)
            rpm -= rng.uniform(200, 500)

        rows_out.append({
            "timestamp": ts.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "temperature": round(_clamp(temp, 40, 120), 2),
            "pressure": round(_clamp(pressure, 85, 130), 2),
            "vibration": round(_clamp(vibration, 0.05, 2.5), 3),
            "humidity": round(_clamp(humidity, 15, 95), 2),
            "flow_rate": round(_clamp(flow_rate, 5, 35), 2),
            "voltage": round(_clamp(voltage, 180, 260), 2),
            "current": round(_clamp(current, 2, 20), 2),
            "rpm": int(_clamp(rpm, 600, 2200)),
            "anomaly": anomaly,
        })

    return rows_out


@router.post("/generate")
def generate_dataset(
    rows: int = Query(500, ge=10, le=20000),
    interval_seconds: int = Query(10, ge=1, le=3600),
    anomaly_rate: float = Query(0.06, ge=0.0, le=0.5),
    seed: Optional[int] = Query(None),
):
    csv_path = Path(__file__).resolve().parents[3] / CSV_NAME
    rows_out = _synth_rows(
        rows=rows,
        interval_seconds=interval_seconds,
        anomaly_rate=anomaly_rate,
        seed=seed,
    )
    _write_csv(csv_path, rows_out)

    return {
        "rows": rows,
        "path": str(csv_path),
        "preview": rows_out[-10:],
    }


@router.post("/generate-normal")
def generate_normal_dataset(
    rows: int = Query(2000, ge=10, le=20000),
    interval_seconds: int = Query(10, ge=1, le=3600),
    seed: Optional[int] = Query(None),
):

    csv_path = Path(__file__).resolve().parents[3] / CSV_NAME
    rows_out = _synth_rows(
        rows=rows,
        interval_seconds=interval_seconds,
        anomaly_rate=0.0,
        seed=seed,
    )
    _write_csv(csv_path, rows_out)

    return {
        "rows": rows,
        "path": str(csv_path),
        "preview": rows_out[-10:],
    }


@router.post("/generate-anomaly")
def generate_anomaly_dataset(
    rows: int = Query(1000, ge=50, le=5000),
    interval_seconds: int = Query(10, ge=1, le=3600),
    seed: Optional[int] = Query(None),
):

    rng = random.Random(seed) if seed is not None else random

    # Baseline values
    temp = 70.0
    vibration = 0.3
    pressure = 102.0
    humidity = 45.0
    rpm = 1500.0
    voltage = 230.0
    current = 8.0

    start_time = datetime.now(timezone.utc) - timedelta(seconds=interval_seconds * (rows - 1))
    rows_out = []

    for i in range(rows):
        ts = start_time + timedelta(seconds=i * interval_seconds)

        if i < rows // 3:
            temp += rng.gauss(0, 0.2)
            vibration += rng.gauss(0, 0.01)
            pressure += rng.gauss(0, 0.1)
            rpm += rng.gauss(0, 5)
            anomaly = 0
        elif i < (2 * rows) // 3:
            temp += rng.gauss(0.3, 0.4)
            vibration += rng.gauss(0.1, 0.05)
            pressure += rng.gauss(0.5, 0.3)
            rpm += rng.gauss(10, 20)
            anomaly = 0
        else:
            temp += rng.uniform(2, 5)
            vibration += rng.uniform(0.5, 2)
            pressure += rng.uniform(5, 10)
            rpm += rng.uniform(50, 200)
            anomaly = 1

        humidity += rng.gauss(0, 1)
        voltage += rng.gauss(0, 2)
        current += rng.gauss(0, 0.5)

        rows_out.append({
            "timestamp": ts.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "temperature": round(float(temp), 2),
            "vibration": round(float(max(0, vibration)), 3),
            "pressure": round(float(pressure), 2),
            "humidity": round(float(humidity), 2),
            "rpm": int(max(0, round(float(rpm), 0))),
            "voltage": round(float(voltage), 2),
            "current": round(float(current), 2),
            "anomaly": anomaly,
        })

    csv_path = Path(__file__).resolve().parents[3] / ANOMALY_CSV_NAME
    _write_csv(csv_path, rows_out)

    return {
        "rows": rows,
        "path": str(csv_path),
        "preview": rows_out[-10:],
    }
