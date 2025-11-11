from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.db import init_db
from routes import auth_routes, attendance_routes, qr_routes, facial_routes, location_routes, face_registration_routes

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Register routes
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(attendance_routes.router, prefix="/attendance", tags=["attendance"])
app.include_router(qr_routes.router, prefix="/qr", tags=["qr"])
app.include_router(facial_routes.router, prefix="/facial", tags=["facial"])
app.include_router(location_routes.router, prefix="/location", tags=["location"])
app.include_router(face_registration_routes.router, prefix="/face", tags=["face-registration"])  # NEW LINE

@app.get("/")
def read_root():
    return {"message": "Smart Attendance API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
