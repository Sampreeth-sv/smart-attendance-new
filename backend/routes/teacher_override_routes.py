from fastapi import APIRouter, Depends, HTTPException
from utils.db import SessionLocal
from models.user_model import User
from models.attendance_model import Attendance
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/override")
def manual_attendance_override(payload: dict, db=Depends(get_db)):
    try:
        teacher_name = payload.get("teacher_name")
        subject = payload.get("subject")
        usns = payload.get("usns", [])

        if not teacher_name or not subject or not usns:
            raise HTTPException(status_code=400, detail="Missing data")

        marked = []
        for usn in usns:
            user = db.query(User).filter(User.usn == usn).first()
            if not user:
                continue

            attendance = Attendance(
                user_usn=user.usn,
                classroom_id=1,
                subject=subject,
                qr_match=False,
                location_match=False,
                face_match=False,
                marked_by_teacher=True,
                timestamp=datetime.now()
            )
            db.add(attendance)
            marked.append(usn)

        db.commit()
        return {"message": "Attendance overridden successfully", "marked": marked}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
