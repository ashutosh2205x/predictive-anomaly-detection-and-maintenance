import pandas as pd
import numpy as np
from datetime import datetime, timedelta

rows = []
time = datetime.now()

temp = 60
vibration = 0.2
pressure = 101

for i in range(300):
    # Normal drift
    temp += np.random.normal(0, 0.3)
    vibration += np.random.normal(0, 0.02)
    pressure += np.random.normal(0, 0.2)

    anomaly = 0

    # Inject anomaly
    if np.random.rand() > 0.92:
        # temp += np.random.uniform(5, 10)
        temp += np.random.normal(0.5, 0.3)
        vibration += np.random.uniform(0.5, 1.0)
        pressure += np.random.uniform(3, 6)
        anomaly = 1

    rows.append({
        "timestamp": time + timedelta(seconds=i*10),
        "temperature": round(temp, 2),
        "vibration": round(vibration, 3),
        "pressure": round(pressure, 2),
        "anomaly": anomaly
    })

df = pd.DataFrame(rows)
df.to_csv("sensor_data.csv", index=False)

print("CSV generated!")