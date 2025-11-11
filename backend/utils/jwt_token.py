from datetime import datetime, timedelta
from fastapi import HTTPException, Header
import jwt
from utils.config import JWT_SECRET, JWT_ALGORITHM

def create_access_token(data: dict, expires_minutes: int = 60*24):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_access_token(token: str):
    """Decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def verify_token(authorization: str = Header(None)):
    """
    Verify JWT token from Authorization header
    Used as a dependency in FastAPI routes
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Check if it starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    # Extract token
    token = authorization.split(" ")[1]
    
    # Decode and verify token
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload
