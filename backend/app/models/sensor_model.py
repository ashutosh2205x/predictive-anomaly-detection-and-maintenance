from pydantic import BaseModel

class SensorData(BaseModel):
    temperature: float
    vibration: float
    pressure: float