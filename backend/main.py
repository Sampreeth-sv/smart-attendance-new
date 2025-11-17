from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Routers
from routes import (
    auth_routes,
    attendance_routes,
    facial_routes,
    qr_routes,
    location_routes,
    face_registration_routes,
    teacher_override_routes
)

# Initialize FastAPI
app = FastAPI(title="Smart Attendance System")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(attendance_routes.router, prefix="/attendance", tags=["Attendance"])
app.include_router(facial_routes.router, prefix="/facial", tags=["Facial Recognition"])
app.include_router(qr_routes.router, prefix="/qr", tags=["QR"])
app.include_router(location_routes.router, prefix="/location", tags=["Location"])
app.include_router(face_registration_routes.router, prefix="/face-registration", tags=["Face Registration"])
app.include_router(teacher_override_routes.router, prefix="/teacher", tags=["Teacher Override"])

# Root Endpoint
@app.get("/")
def home():
    return {"message": "Smart Attendance Backend Running ✅"}

# Run App (Local)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
