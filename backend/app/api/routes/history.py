from fastapi import APIRouter
from app.db.mongo import collection

router = APIRouter()

@router.get("/history")
def get_history():
    data = list(collection.find({}, {"_id": 0}).limit(200))
    return data