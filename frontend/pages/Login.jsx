import { useState } from "react";

function Login({ onLogin, error }) {
  const [role, setRole] = useState("student");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate inputs
    if (!username.trim()) {
      alert("Please enter your username");
      return;
    }

    if (!password.trim()) {
      alert("Please enter your password");
      return;
    }

    // Set loading state
    setIsLoading(true);

    // Call the login handler from App.jsx
    await onLogin(username, password, role);

    // Reset loading state
    setIsLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Smart Attendance System</h2>
        <p className="login-subtitle">Please login to continue</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="role">Select Role</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="form-control"
              disabled={isLoading}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-control"
              disabled={isLoading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-control"
              disabled={isLoading}
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn-login"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="login-info">
          <p>💡 Use your credentials to access the system</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
