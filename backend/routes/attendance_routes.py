from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils.db import SessionLocal
from models.attendance_model import Attendance
from models.user_model import User
from utils.jwt_token import verify_token
from datetime import datetime

router = APIRouter()

class MarkAttendanceSchema(BaseModel):
    session_id: str
    student_id: str
    location: dict

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/mark")
def mark_attendance(payload: MarkAttendanceSchema, token: dict = Depends(verify_token), db = Depends(get_db)):
    """Mark attendance for a student"""
    
    try:
        user = db.query(User).filter(User.name == payload.student_id).first()
        
        if not user:
            print(f"❌ User not found: {payload.student_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get subject from session (you'll need to import qr_routes to access active_sessions)
        from routes.qr_routes import active_sessions
        session_data = active_sessions.get(payload.session_id, {})
        subject = session_data.get("subject", "Unknown")
        
        attendance = Attendance(
            user_usn=user.usn,
            classroom_id=1,
            subject=subject,  # Now using actual subject from session
            qr_match=True,
            location_match=True,
            face_match=True,
            marked_by_teacher=False,
            timestamp=datetime.now()
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        print(f"✅ Attendance marked successfully for {payload.student_id} in {subject}")
        
        return {
            "success": True,
            "message": "Attendance marked successfully",
            "attendance_id": attendance.id
        }
        
    except Exception as e:
        print(f"❌ Error marking attendance: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/history/{student_name}")
def attendance_history(student_name: str, token: dict = Depends(verify_token), db = Depends(get_db)):
    """Get attendance history for a student"""
    
    try:
        # Find user by name
        user = db.query(User).filter(User.name == student_name).first()
        
        if not user:
            return {
                "total_records": 0,
                "attended": 0,
                "records": []
            }
        
        # Get all attendance records for this user
        recs = db.query(Attendance).filter(Attendance.user_usn == user.usn).order_by(Attendance.timestamp.desc()).all()
        
        total = len(recs)
        attended = sum(1 for r in recs if not r.marked_by_teacher or (r.qr_match or r.location_match or r.face_match))
        
        return {
            "total_records": total,
            "attended": attended,
            "records": [{
                "id": r.id,
                "classroom_id": r.classroom_id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "qr": r.qr_match,
                "loc": r.location_match,
                "face": r.face_match,
                "by_teacher": r.marked_by_teacher,
                "subject": r.subject or "N/A"
            } for r in recs]
        }
        
    except Exception as e:
        print(f"❌ Error fetching attendance history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/session/{session_id}")
def get_session_attendance(session_id: str, token: dict = Depends(verify_token), db = Depends(get_db)):
    """Get all attendance records for a specific session"""
    
    try:
        # Get all attendance records for this session
        # For now, we'll get recent records (last 2 hours)
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        recs = db.query(Attendance).filter(
            Attendance.timestamp >= cutoff_time
        ).order_by(Attendance.timestamp.desc()).all()
        
        # Get user details for each record
        records_with_users = []
        for rec in recs:
            user = db.query(User).filter(User.usn == rec.user_usn).first()
            if user:
                records_with_users.append({
                    "id": rec.id,
                    "student_name": user.name,
                    "usn": user.usn,
                    "timestamp": rec.timestamp.isoformat() if rec.timestamp else None,
                    "qr": rec.qr_match,
                    "location": rec.location_match,
                    "face": rec.face_match,
                    "by_teacher": rec.marked_by_teacher,
                    "subject": rec.subject or "N/A"
                })
        
        # Calculate stats (mock data - in production, get actual enrollment)
        total_students = 30  # Mock total
        present_count = len(records_with_users)
        percentage = (present_count / total_students * 100) if total_students > 0 else 0
        
        return {
            "records": records_with_users,
            "total_students": total_students,
            "present_count": present_count,
            "percentage": percentage
        }
        
    except Exception as e:
        print(f"❌ Error fetching session attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
