from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from utils.db import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_usn = Column(String(20), ForeignKey("users.usn"))
    session_id = Column(String(100), nullable=False)   # ✅ ADD THIS LINE
    classroom_id = Column(Integer)
    subject = Column(String(255), nullable=True)

    qr_match = Column(Boolean, default=False)
    location_match = Column(Boolean, default=False)
    face_match = Column(Boolean, default=False)

    marked_by_teacher = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
