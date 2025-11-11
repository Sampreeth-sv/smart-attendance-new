from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils.db import SessionLocal
from models.user_model import User
from utils.jwt_token import create_access_token
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterSchema(BaseModel):
    usn: str
    name: str
    email: str
    password: str
    is_teacher: bool = False

class LoginSchema(BaseModel):
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(payload: RegisterSchema, db=Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(payload.password)
    user = User(usn=payload.usn, name=payload.name, email=payload.email, password_hash=hashed, is_teacher=payload.is_teacher)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"usn": user.usn, "email": user.email, "is_teacher": user.is_teacher})
    return {"access_token": token, "user": {"usn": user.usn, "name": user.name, "is_teacher": user.is_teacher}}

@router.post("/login")
def login(payload: LoginSchema, db=Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"usn": user.usn, "email": user.email, "is_teacher": user.is_teacher})
    return {"access_token": token, "user": {"usn": user.usn, "name": user.name, "is_teacher": user.is_teacher}}
