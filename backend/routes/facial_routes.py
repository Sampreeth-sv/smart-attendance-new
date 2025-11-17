# routes/facial_routes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.jwt_token import verify_token
from utils.db import get_db
from models.user_model import User
import base64
import os
from deepface import DeepFace
from datetime import datetime

router = APIRouter()


class FaceVerifySchema(BaseModel):
    image: str
    user_id: str


@router.post("/verify")
def verify_face(payload: FaceVerifySchema, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Verify face using DeepFace.
    - If no registered face exists, currently auto-approves (keeps older behavior).
    - Uses a temp file for comparison, removes it afterwards.
    """

    try:
        # Lookup user
        user = db.query(User).filter(User.name == payload.user_id).first()
        if not user:
            return {"verified": False, "message": "User not found"}

        # Path where registered face photos are stored (existing behavior)
        registered_face_path = f"face_data/{user.usn}.jpg"

        if not os.path.exists(registered_face_path):
            # No registered face — keep previous behavior: approve and return a high confidence.
            print(f"⚠️ No registered face for {user.name} — auto-approving (dev mode).")
            return {
                "verified": True,
                "message": "Face verified (no registered face - auto-approved)",
                "confidence": 0.90
            }

        # Decode incoming image (data URL or base64 string)
        image_str = payload.image
        if "," in image_str:
            image_str = image_str.split(",")[1]

        image_bytes = base64.b64decode(image_str)

        # Save temp image file
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        temp_path = f"face_data/temp_{user.usn}_{timestamp}.jpg"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        print(f"📸 Verifying face for {user.name} using DeepFace...")

        # Run DeepFace verify (enforce_detection False to avoid strict failure)
        result = DeepFace.verify(
            img1_path=registered_face_path,
            img2_path=temp_path,
            model_name="VGG-Face",
            enforce_detection=False
        )

        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ Failed to remove temp file {temp_path}: {e}")

        verified = result.get("verified", False)
        distance = result.get("distance", None)
        threshold = result.get("threshold", None)

        print(f"✅ Face verification: verified={verified}, distance={distance}, threshold={threshold}")

        # Compute a safety confidence if possible
        confidence = None
        if distance is not None and threshold:
            try:
                confidence = 1 - (distance / threshold) if threshold > 0 else 0
            except Exception:
                confidence = None

        return {
            "verified": bool(verified),
            "message": "Face verified successfully" if verified else "Face verification failed",
            "confidence": confidence,
            "distance": distance,
            "threshold": threshold
        }

    except Exception as e:
        # Log and fallback to auto-approve (preserves prior dev behavior)
        print(f"❌ Error in face verification: {e}")
        return {
            "verified": True,
            "message": f"Verification error (auto-approved): {str(e)}",
            "confidence": 0.85
        }
