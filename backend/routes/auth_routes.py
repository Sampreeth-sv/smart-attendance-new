# routes/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.db import get_db
from models.user_model import User
from utils.jwt_token import create_access_token
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# 📘 Schemas
# ---------------------------
class RegisterSchema(BaseModel):
    usn: str
    name: str
    email: str
    password: str
    is_teacher: bool = False


class LoginSchema(BaseModel):
    email: str
    password: str


# ---------------------------
# 📝 Register User
# ---------------------------
@router.post("/register")
def register(payload: RegisterSchema, db: Session = Depends(get_db)):

    # Check if email taken
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed = pwd_context.hash(payload.password)

    user = User(
        usn=payload.usn,
        name=payload.name,
        email=payload.email,
        password_hash=hashed,
        is_teacher=payload.is_teacher,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "usn": user.usn,
        "email": user.email,
        "is_teacher": user.is_teacher
    })

    return {
        "access_token": token,
        "user": {
            "usn": user.usn,
            "name": user.name,
            "email": user.email,
            "is_teacher": user.is_teacher
        }
    }


# ---------------------------
# 🔐 Login (support plain + hashed)
# ---------------------------
@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Handle normal hashed password
    try:
        password_ok = pwd_context.verify(payload.password, user.password_hash)

    except UnknownHashError:
        # HASH missing / old DB using plain password
        password_ok = (payload.password == user.password_hash)

    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Auto-convert old plain password → bcrypt
    try:
        if not user.password_hash.startswith("$2b$"):  # bcrypt prefix
            user.password_hash = pwd_context.hash(payload.password)
            db.add(user)
            db.commit()
    except:
        pass

    # Create JWT
    token = create_access_token({
        "usn": user.usn,
        "email": user.email,
        "is_teacher": user.is_teacher
    })

    return {
        "access_token": token,
        "user": {
            "usn": user.usn,
            "name": user.name,
            "email": user.email,
            "is_teacher": user.is_teacher
        }
    }
    
