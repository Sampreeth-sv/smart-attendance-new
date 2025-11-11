from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils.db import SessionLocal
from models.classroom_model import Classroom
import math

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LocationPayload(BaseModel):
    classroom_id: int
    lat: float
    lon: float

def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in meters
    R = 6371000
    import math
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@router.post("/verify")
def verify_location(payload: LocationPayload, db=Depends(get_db)):
    classroom = db.query(Classroom).filter(Classroom.id == payload.classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    dist_m = haversine_km(payload.lat, payload.lon, classroom.lat, classroom.lon)
    allowed_radius = 50  # meters; tune as needed
    return {"distance_m": dist_m, "within_radius": dist_m <= allowed_radius}
