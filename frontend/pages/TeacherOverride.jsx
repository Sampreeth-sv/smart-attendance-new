import { useState, useEffect } from "react";

function TeacherOverride({ teacher, onClose }) {
  const [students, setStudents] = useState([]);
  const [selected, setSelected] = useState([]);
  const [subject, setSubject] = useState("");
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(""); // ✅ NEW

  // Subjects mapped by teacher
  const subjectsByTeacher = {
    T001: [
      "Software Engineering and Project Management",
      "Computer Networks",
      "Theory of Computation"
    ],
    T002: [
      "Web Technology Lab",
      "Artificial Intelligence",
      "Research Methodology and IPR"
    ]
  };

  // Use teacher.usn (CORRECT)
  const teacherSubjects = subjectsByTeacher[teacher.usn] || [];

  // Fetch student list
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const token = localStorage.getItem("token");

        const res = await fetch("http://localhost:5000/attendance/students", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        const data = await res.json();
        setStudents(data.students || []);
      } catch (err) {
        console.error("Error fetching students:", err);
      }
    };

    fetchStudents();
  }, []);

  const handleCheckbox = (usn) => {
    setSelected((prev) =>
      prev.includes(usn) ? prev.filter((id) => id !== usn) : [...prev, usn]
    );
  };

  const handleOverride = async () => {
    if (!subject || selected.length === 0) {
      alert("⚠️ Select at least one student and subject!");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      const res = await fetch("http://localhost:5000/teacher/mark", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          usns: selected,
          subject: subject,
          classroom_id: 1
        })
      });

      const data = await res.json();

      if (res.ok) {
        // ✅ SUCCESS MESSAGE (INSTEAD OF ALERT)
        setSuccessMsg(`Attendance overridden for: ${selected.join(", ")}`);
        setSelected([]);

        // Auto-hide popup after 3 seconds
        setTimeout(() => {
          setSuccessMsg("");
        }, 3000);
      } else {
        alert("❌ Error overriding attendance: " + (data.detail || "Unknown error"));
      }
    } catch (err) {
      alert("❌ Server error.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="override-modal"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0,0,0,0.6)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000
      }}
    >
      <div
        className="card"
        style={{
          backgroundColor: "white",
          padding: "20px",
          width: "90%",
          maxWidth: "600px",
          borderRadius: "10px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.2)"
        }}
      >
        <h3>✏️ Manual Attendance Override</h3>

        <p>
          Teacher: <strong>{teacher.usn}</strong>
        </p>

        <label>Select Subject:</label>
        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          style={{
            width: "100%",
            marginBottom: "10px",
            padding: "5px",
            borderRadius: "5px"
          }}
        >
          <option value="">-- Choose Subject --</option>
          {teacherSubjects.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        {/* ✅ SUCCESS POPUP BOX HERE */}
        {successMsg && (
          <div
            style={{
              backgroundColor: "#d4edda",
              color: "#155724",
              padding: "10px 15px",
              borderRadius: "6px",
              marginBottom: "12px",
              border: "1px solid #c3e6cb",
              fontWeight: "500",
              textAlign: "center"
            }}
          >
            {successMsg}
          </div>
        )}

        <h4>Student List</h4>
        <div
          className="student-list"
          style={{
            maxHeight: "300px",
            overflowY: "auto",
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "10px"
          }}
        >
          {students.length === 0 ? (
            <p>Loading students...</p>
          ) : (
            students.map((s) => (
              <div
                key={s.usn}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "6px"
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(s.usn)}
                  onChange={() => handleCheckbox(s.usn)}
                  style={{ marginRight: "10px" }}
                />
                <span>
                  {s.name} ({s.usn})
                </span>
              </div>
            ))
          )}
        </div>

        <div
          className="actions"
          style={{
            marginTop: "15px",
            display: "flex",
            justifyContent: "space-between"
          }}
        >
          <button
            onClick={handleOverride}
            disabled={loading}
            className="btn-success"
            style={{
              padding: "10px 20px",
              borderRadius: "5px",
              border: "none",
              backgroundColor: "#28a745",
              color: "white"
            }}
          >
            {loading ? "Marking..." : "✅ Mark Selected Present"}
          </button>

          <button
            onClick={onClose}
            className="btn-danger"
            style={{
              padding: "10px 20px",
              borderRadius: "5px",
              border: "none",
              backgroundColor: "#dc3545",
              color: "white"
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default TeacherOverride;
