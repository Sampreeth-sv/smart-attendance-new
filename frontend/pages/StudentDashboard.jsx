import { useState, useEffect, useRef } from "react";
import QRCode from "react-qr-code";
import AttendanceHistory from "./AttendanceHistory";
import FaceRegistration from "./FaceRegistration";

function StudentDashboard({ user, onLogout }) {
  const [attendanceActive, setAttendanceActive] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [step, setStep] = useState(1);
  
  const [location, setLocation] = useState(null);
  const [locationVerified, setLocationVerified] = useState(false);
  
  const [cameraActive, setCameraActive] = useState(false);
  const [faceVerified, setFaceVerified] = useState(false);
  const videoRef = useRef(null);
  
  const [attendanceMarked, setAttendanceMarked] = useState(false);
  const [markedSessionId, setMarkedSessionId] = useState(null); // Track only the last marked session
  const [loading, setLoading] = useState(false);
  
  const [showHistory, setShowHistory] = useState(false);
  const [showFaceRegistration, setShowFaceRegistration] = useState(false);

  // Check for active sessions
  useEffect(() => {
    if (showHistory || showFaceRegistration) return;

    const checkActiveSession = async () => {
      try {
        const response = await fetch("http://localhost:5000/qr/active-session");

        if (response.ok) {
          const data = await response.json();
          if (data.active) {
            // If this is a NEW session (different from the one we just marked)
            if (data.session_id !== markedSessionId) {
              setAttendanceActive(true);
              setCurrentSession(data);
              
              // Reset states for new session
              if (!currentSession || currentSession.session_id !== data.session_id) {
                setAttendanceMarked(false);
                setStep(1);
                setLocation(null);
                setLocationVerified(false);
                setCameraActive(false);
                setFaceVerified(false);
              }
            } else {
              // This is the same session we just completed
              setAttendanceActive(false);
            }
          } else {
            setAttendanceActive(false);
            setCurrentSession(null);
          }
        }
      } catch (error) {
        console.error("Error checking session:", error);
      }
    };

    checkActiveSession();
    const interval = setInterval(checkActiveSession, 3000);
    return () => clearInterval(interval);
  }, [showHistory, showFaceRegistration, currentSession, markedSessionId]);

  if (showHistory) {
    return <AttendanceHistory user={user} onBack={() => setShowHistory(false)} />;
  }

  if (showFaceRegistration) {
    return (
      <FaceRegistration 
        user={user} 
        onBack={() => setShowFaceRegistration(false)}
        onSuccess={() => {
          setShowFaceRegistration(false);
          alert("✅ Face registered! You can now use AI face verification for attendance.");
        }}
      />
    );
  }

  const handleGetLocation = () => {
    setLoading(true);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          setLocation(coords);
          setLocationVerified(true);
          setStep(3);
          setLoading(false);
          alert("✅ Location verified!");
        },
        (error) => {
          alert("❌ Location access denied. Please enable location services.");
          setLoading(false);
        }
      );
    } else {
      alert("❌ Geolocation is not supported by your browser");
      setLoading(false);
    }
  };

  const handleOpenCamera = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("❌ Your browser doesn't support camera access");
      return;
    }
    
    if (!videoRef.current) {
      alert("Video element not ready. Please try again.");
      return;
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user" 
        } 
      });
      
      videoRef.current.srcObject = stream;
      
      videoRef.current.onloadedmetadata = () => {
        videoRef.current.play()
          .then(() => {
            setCameraActive(true);
          })
          .catch(err => {
            alert("Error playing video: " + err.message);
          });
      };
    } catch (error) {
      let errorMessage = "Camera access failed: ";
      
      switch (error.name) {
        case 'NotAllowedError':
        case 'PermissionDeniedError':
          errorMessage += "Permission denied. Please allow camera access.";
          break;
        case 'NotFoundError':
        case 'DevicesNotFoundError':
          errorMessage += "No camera found. Please connect a camera.";
          break;
        case 'NotReadableError':
        case 'TrackStartError':
          errorMessage += "Camera is being used by another application.";
          break;
        default:
          errorMessage += error.message || "Unknown error";
      }
      
      alert("❌ " + errorMessage);
    }
  };

  const handleCaptureFace = async () => {
    if (!cameraActive) {
      alert("Please open camera first!");
      return;
    }

    setLoading(true);

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d').drawImage(videoRef.current, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg');

    try {
      const token = localStorage.getItem("token");
      
      const response = await fetch("http://localhost:5000/facial/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          image: imageData,
          user_id: user.name
        })
      });

      const data = await response.json();

      if (response.ok && data.verified) {
        setFaceVerified(true);
        alert("✅ Face verified!");
        await markAttendance();
      } else {
        alert("❌ Face verification failed. Please try again.");
      }
    } catch (error) {
      alert("Error during face verification");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const markAttendance = async () => {
    try {
      const token = localStorage.getItem("token");
      
      const response = await fetch("http://localhost:5000/attendance/mark", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          location: location,
          student_id: user.name
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Store this session ID as the last marked one
        setMarkedSessionId(currentSession.session_id);
        setAttendanceMarked(true);
        setStep(4);
        
        // Stop camera
        if (videoRef.current && videoRef.current.srcObject) {
          videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
        
        alert("🎉 Attendance marked successfully!");
      } else {
        alert(data.message || "Failed to mark attendance");
      }
    } catch (error) {
      alert("Error marking attendance");
      console.error(error);
    }
  };

  const handleStartQRVerification = () => {
    setStep(2);
  };

  const handleBackToDashboard = () => {
    setAttendanceMarked(false);
    setStep(1);
    setLocation(null);
    setLocationVerified(false);
    setCameraActive(false);
    setFaceVerified(false);
    // Don't clear markedSessionId - keep it to prevent re-showing same session
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Welcome, {user.name}!</h2>
        <button onClick={onLogout} className="btn-danger">Logout</button>
      </div>

      <div className="card">
        <h3>📱 Student Dashboard</h3>
        <p>Mark your attendance when the session is active</p>
        
        <button onClick={() => setShowHistory(true)} className="btn mt-2" style={{ width: "100%" }}>
          📊 View Attendance History
        </button>

        <button 
          onClick={() => setShowFaceRegistration(true)} 
          className="btn mt-2" 
          style={{ width: "100%", background: "#28a745", color: "white" }}
        >
          📸 Register Face for AI Verification
        </button>
      </div>

      {!attendanceActive ? (
        <div className="card info-message">
          <h3>
            {markedSessionId 
              ? "✅ Attendance Completed" 
              : "⏳ No Active Attendance Session"}
          </h3>
          <p>
            {markedSessionId
              ? "Waiting for new attendance sessions..."
              : "Waiting for teacher to start attendance..."}
          </p>
          <p className="mt-2">
            New sessions will appear here automatically.
          </p>
        </div>
      ) : attendanceMarked ? (
        <div className="card success-message">
          <h2>✅ Attendance Marked!</h2>
          <p>Subject: {currentSession.subject}</p>
          <p>Your attendance has been successfully recorded.</p>
          <button onClick={handleBackToDashboard} className="btn-success mt-3">
            ✓ Done - Check for Next Session
          </button>
        </div>
      ) : (
        <div className="attendance-section card">
          <h3>📋 Active Session: {currentSession?.subject}</h3>
          
          {step === 1 && (
            <div className="qr-step">
              <h4>Step 1: QR Code Verification</h4>
              <p>Scan this QR code or click verify</p>
              
              <div className="qr-display">
                <QRCode 
                  value={JSON.stringify(currentSession)} 
                  size={200}
                  style={{ margin: "20px auto", display: "block" }}
                />
              </div>
              
              <button onClick={handleStartQRVerification} className="btn-success mt-3">
                ✓ Verify QR Code
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="location-step">
              <h4>Step 2: Location Verification</h4>
              <p>We need to verify you're in the classroom</p>
              
              {!locationVerified ? (
                <button 
                  onClick={handleGetLocation} 
                  disabled={loading}
                  className="btn-success mt-3"
                >
                  {loading ? "Verifying..." : "📍 Verify Location"}
                </button>
              ) : (
                <div className="success-message mt-2">
                  <p>✅ Location Verified</p>
                  <p>Lat: {location.latitude.toFixed(6)}</p>
                  <p>Lng: {location.longitude.toFixed(6)}</p>
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="face-step">
              <h4>Step 3: Face Verification</h4>
              <p>Capture your face for attendance</p>
              
              <div style={{ textAlign: "center", marginTop: "20px" }}>
                <video 
                  ref={videoRef} 
                  autoPlay 
                  playsInline
                  muted
                  style={{ 
                    width: "100%", 
                    maxWidth: "400px", 
                    borderRadius: "10px",
                    border: "3px solid #667eea",
                    display: cameraActive ? "block" : "none",
                    margin: "0 auto 20px auto"
                  }}
                />
                
                {!cameraActive && (
                  <div style={{
                    width: "100%",
                    maxWidth: "400px",
                    height: "300px",
                    backgroundColor: "#f0f0f0",
                    borderRadius: "10px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 20px auto",
                    border: "2px dashed #ccc"
                  }}>
                    <p style={{ color: "#666", fontSize: "18px" }}>📷 Camera Off</p>
                  </div>
                )}
              </div>
              
              {!cameraActive ? (
                <button onClick={handleOpenCamera} className="btn-success mt-3">
                  📷 Open Camera
                </button>
              ) : (
                <button 
                  onClick={handleCaptureFace}
                  disabled={loading}
                  className="btn-success mt-3"
                >
                  {loading ? "Verifying..." : "📸 Capture & Verify"}
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StudentDashboard;
