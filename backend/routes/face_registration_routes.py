from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from utils.jwt_token import verify_token
from utils.db import SessionLocal
from models.user_model import User
import base64
import os
from PIL import Image
from io import BytesIO

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register-face")
async def register_face(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token),
    db = Depends(get_db)
):
    """Register a student's face for future verification"""
    try:
        # Get USN from token
        user_usn = token.get("usn")
        
        if not user_usn:
            raise HTTPException(status_code=400, detail="Invalid token: missing USN")
        
        # Find user by USN
        user = db.query(User).filter(User.usn == user_usn).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_usn}")
        
        # Read and save the image
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        # Create face_data directory
        os.makedirs("face_data", exist_ok=True)
        
        # Save image with USN as filename
        image_path = f"face_data/{user.usn}.jpg"
        image.save(image_path)
        
        print(f"✅ Face registered for {user.name} ({user.usn})")
        
        return {
            "success": True,
            "message": "Face registered successfully",
            "user": user.name,
            "usn": user.usn
        }
        
    except Exception as e:
        print(f"❌ Error registering face: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-face-base64")
async def register_face_base64(
    image_data: dict,
    token: dict = Depends(verify_token),
    db = Depends(get_db)
):
    """Register face from base64 encoded image (for webcam capture)"""
    try:
        # Get USN from token
        user_usn = token.get("usn")
        
        print(f"🔍 Token data: {token}")
        print(f"🔍 User USN from token: {user_usn}")
        
        if not user_usn:
            raise HTTPException(status_code=400, detail="Invalid token: missing USN")
        
        # Find user by USN
        user = db.query(User).filter(User.usn == user_usn).first()
        
        if not user:
            print(f"❌ User not found with USN: {user_usn}")
            raise HTTPException(status_code=404, detail=f"User not found: {user_usn}")
        
        print(f"✅ Found user: {user.name} ({user.usn})")
        
        # Decode base64 image
        image_str = image_data.get("image", "")
        if "," in image_str:
            image_str = image_str.split(",")[1]
        
        image_bytes = base64.b64decode(image_str)
        image = Image.open(BytesIO(image_bytes))
        
        # Create directory and save
        os.makedirs("face_data", exist_ok=True)
        image_path = f"face_data/{user.usn}.jpg"
        image.save(image_path)
        
        print(f"✅ Face image saved to: {image_path}")
        print(f"✅ Face registered for {user.name} ({user.usn})")
        
        return {
            "success": True,
            "message": "Face registered successfully",
            "user": user.name,
            "usn": user.usn
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error registering face: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
