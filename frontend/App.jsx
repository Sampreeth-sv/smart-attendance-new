import { useState, useEffect } from "react";
import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import "./styles/App.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔍 Check for existing session when app loads
  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    const username = localStorage.getItem("username");
    const usn = localStorage.getItem("usn");

    if (token && role && username && usn) {
      setUser({ role, name: username, usn, token });
    }

    // 👇 Debug log to verify user info from localStorage
    console.log("Loaded from localStorage:", { token, role, username, usn });

    setLoading(false);
  }, []);

  // 🧩 Handle login with backend authentication
  const handleLogin = async (username, password, role) => {
    setError("");

    try {
      const response = await fetch("http://localhost:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: username,
          password: password,
        }),
      });

      const data = await response.json();
      console.log("Login response:", data); // 👈 Debug log to see backend response

      if (response.ok) {
        // ✅ Store login details in localStorage
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.user.is_teacher ? "teacher" : "student");
        localStorage.setItem("username", data.user.name);
        localStorage.setItem("usn", data.user.usn); // ✅ Store USN too

        setUser({
          role: data.user.is_teacher ? "teacher" : "student",
          name: data.user.name,
          usn: data.user.usn,
          token: data.access_token,
        });

        console.log("Logged in user:", data.user); // 👈 Confirm backend returned usn
      } else {
        const msg = data.detail || data.message || "Login failed. Please try again.";
        setError(msg);
        alert(msg);
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Unable to connect to server. Please try again later.");
      alert("Error connecting to server. Make sure the backend is running.");
    }
  };

  // 🚪 Handle logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    localStorage.removeItem("usn");
    setUser(null);
    setError("");
  };

  // 🕒 Show loading screen while checking session
  if (loading) {
    return (
      <div className="loading-container">
        <h2>Loading...</h2>
      </div>
    );
  }

  // 🔐 If not logged in, show login page
  if (!user) {
    return <Login onLogin={handleLogin} error={error} />;
  }

  // 🎓 Render dashboard based on user role
  return (
    <>
      {user.role === "student" && (
        <StudentDashboard user={user} onLogout={handleLogout} />
      )}
      {user.role === "teacher" && (
        <TeacherDashboard user={user} onLogout={handleLogout} />
      )}
    </>
  );
}

export default App;
