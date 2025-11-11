from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils.db import SessionLocal
from utils.jwt_token import verify_token
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for active sessions (in production, use Redis or database)
active_sessions = {}

class QRGenerateSchema(BaseModel):
    subject: str
    teacher_id: str

class QRStopSchema(BaseModel):
    session_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate")
def generate_qr(payload: QRGenerateSchema, token: str = Depends(verify_token)):
    """Generate a new QR code session for attendance"""
    session_id = str(uuid.uuid4())
    
    active_sessions[session_id] = {
        "subject": payload.subject,
        "teacher_id": payload.teacher_id,
        "created_at": datetime.now().isoformat(),
        "active": True
    }
    
    return {
        "message": "QR session created",
        "session_id": session_id,
        "subject": payload.subject
    }

@router.post("/stop")
def stop_qr(payload: QRStopSchema, token: str = Depends(verify_token)):
    """Stop an active QR code session"""
    if payload.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    active_sessions[payload.session_id]["active"] = False
    
    return {
        "message": "QR session stopped",
        "session_id": payload.session_id
    }

@router.get("/verify/{session_id}")
def verify_qr_session(session_id: str):
    """Verify if a QR session is still active"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if not session["active"]:
        raise HTTPException(status_code=400, detail="Session expired")
    
    return {
        "valid": True,
        "subject": session["subject"],
        "teacher_id": session["teacher_id"]
    }

@router.get("/active-session")
def get_active_session():  # Removed token dependency
    """Check if there's an active attendance session - Public endpoint"""
    # Find the most recent active session
    for session_id, session_data in active_sessions.items():
        if session_data.get("active"):
            return {
                "active": True,
                "session_id": session_id,
                "subject": session_data["subject"],
                "teacher_id": session_data["teacher_id"]
            }
    
    return {
        "active": False
    }
