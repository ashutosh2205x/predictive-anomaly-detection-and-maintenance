from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["iot_db"]
collection = db["sensor_data"]