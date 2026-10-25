
from flask import Flask, jsonify, request, render_template_string
import sqlite3
import requests

app = Flask(__name__)

DATABASE = "students.db"
CLASSMATE_API_URL = "https://jasminerose-2.onrender.com"


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def student_to_dict(student):
    return dict(student)


# ==========================================
# HOME PAGE AND CSS DESIGN
# ==========================================
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Information System</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
        }

        header {
            background: #164e9b;
            color: white;
            padding: 25px 5%;
        }

        header h1 {
            margin: 0 0 8px;
        }

        header p {
            margin: 0;
            color: #dbeafe;
        }

        .container {
            max-width: 1250px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 18px;
            margin-bottom: 25px;
        }

        .stat-card, .panel {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
        }

        .stat-card h3 {
            margin: 0 0 10px;
            color: #64748b;
            font-size: 14px;
        }

        .stat-card p {
            margin: 0;
            color: #164e9b;
            font-size: 27px;
            font-weight: bold;
        }

        .layout {
            display: grid;
            grid-template-columns: 320px minmax(0, 1fr);
            gap: 20px;
            align-items: start;
        }

        h2 {
            margin-top: 0;
            font-size: 20px;
        }

        label {
            display: block;
            font-weight: bold;
            margin: 14px 0 6px;
            font-size: 14px;
        }

        input, select {
            width: 100%;
            padding: 11px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            font-size: 14px;
            background: white;
        }

        input:focus, select:focus {
            outline: 2px solid #93c5fd;
            border-color: #2563eb;
        }

        button {
            border: none;
            padding: 10px 14px;
            border-radius: 7px;
            color: white;
            cursor: pointer;
            font-size: 13px;
            margin: 5px 3px 0 0;
        }

        button:hover {
            opacity: 0.85;
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .primary {
            background: #164e9b;
        }

        .secondary {
            background: #64748b;
        }

        .edit {
            background: #d97706;
        }

        .delete {
            background: #dc2626;
        }

        .api-button {
            background: #0f766e;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        th, td {
            padding: 12px 10px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: #eff6ff;
            color: #164e9b;
        }

        tr:hover td {
            background: #f8fafc;
        }

        .message {
            display: none;
            margin-bottom: 18px;
            padding: 12px;
            border-radius: 7px;
        }

        .success {
            display: block;
            color: #166534;
            background: #dcfce7;
        }

        .error {
            display: block;
            color: #991b1b;
            background: #fee2e2;
        }

        .api-output {
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            background: #0f172a;
            color: #dbeafe;
            padding: 16px;
            border-radius: 8px;
            max-height: 350px;
            overflow: auto;
            font-size: 13px;
        }

        .footer {
            text-align: center;
            color: #64748b;
            padding: 25px;
        }

        @media (max-width: 850px) {
            .layout {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>Student Information System</h1>
    <p>Flask API and SQLite Database Management</p>
</header>

<main class="container">

    <div id="message" class="message" role="status"></div>

    <section class="stats">
        <div class="stat-card">
            <h3>Total Students</h3>
            <p id="totalStudents">0</p>
        </div>

        <div class="stat-card">
            <h3>Database</h3>
            <p style="font-size: 20px;">SQLite</p>
        </div>

        <div class="stat-card">
            <h3>Operations</h3>
            <p style="font-size: 20px;">CRUD</p>
        </div>
    </section>

    <section class="layout">

        <!-- ADD AND EDIT FORM -->
        <div class="panel">
            <h2 id="formTitle">Add Student</h2>

            <form id="studentForm">
                <input type="hidden" id="recordId">

                <label for="student_id">Student ID</label>
                <input
                    type="text"
                    id="student_id"
                    placeholder="e.g. 2026-00130"
                    required
                >

                <label for="name">Full Name</label>
                <input
                    type="text"
                    id="name"
                    placeholder="Enter full name"
                    required
                >

                <label for="program">Program</label>
                <select id="program" required>
                    <option value="">Select Program</option>
                    <option value="BSIT">BSIT</option>
                    <option value="BSCS">BSCS</option>
                    <option value="BSIS">BSIS</option>
                    <option value="BSBA">BSBA</option>
                </select>

                <label for="year">Year Level</label>
                <select id="year" required>
                    <option value="">Select Year</option>
                    <option value="1">1st Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                    <option value="5">5th Year</option>
                    <option value="6">6th Year</option>
                </select>

                <label for="section">Section</label>
                <select id="section" required>
                    <option value="">Select Section</option>
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                </select>

                <button type="submit" class="primary" id="saveButton">
                    Save Student
                </button>

                <button
                    type="button"
                    class="secondary"
                    id="cancelButton"
                    hidden
                >
                    Cancel Edit
                </button>
            </form>
        </div>

        <!-- STUDENT TABLE -->
        <div class="panel">
            <h2>Student Records</h2>

            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>DB ID</th>
                            <th>Student ID</th>
                            <th>Name</th>
                            <th>Program</th>
                            <th>Year</th>
                            <th>Section</th>
                            <th>Actions</th>
                        </tr>
                    </thead>

                    <tbody id="studentTable">
                        <tr>
                            <td colspan="7">Loading records...</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <button
                type="button"
                class="primary"
                id="refreshButton"
            >
                Refresh Records
            </button>
        </div>

    </section>

    <!-- CLASSMATE API -->
    <section class="panel" style="margin-top: 22px;">
        <h2>Classmate API Records</h2>

        <p>
            Retrieve student records from your classmate's deployed API.
        </p>

        <button
            type="button"
            class="api-button"
            id="classmateButton"
        >
            Load Classmate Records
        </button>

        <pre id="classmateOutput" class="api-output">Click the button to load records.</pre>
    </section>

    <!-- API ENDPOINTS -->
    <section class="panel" style="margin-top: 22px;">
        <h2>API Endpoints</h2>

        <p><a href="/api">/api</a> — API information</p>
        <p><a href="/api/students">/api/students</a> — View all students</p>
        <p><a href="/api/classmate/students">/api/classmate/students</a> — Classmate API</p>
    </section>

</main>

<footer class="footer">
    Student Information System | Flask + SQLite
</footer>

<script>
    const form = document.getElementById("studentForm");
    const message = document.getElementById("message");

    function showMessage(text, type) {
        message.textContent = text;
        message.className = "message " + type;
    }

    function escapeHTML(value) {
        return String(value).replace(/[&<>"']/g, function(character) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;"
            }[character];
        });
    }

    // READ ALL STUDENTS
    async function loadStudents() {
        const table = document.getElementById("studentTable");

        try {
            const response = await fetch("/api/students");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to load students.");
            }

            document.getElementById("totalStudents").textContent = data.length;

            if (data.length === 0) {
                table.innerHTML =
                    '<tr><td colspan="7">No student records found.</td></tr>';
                return;
            }

            table.innerHTML = data.map(function(student) {
                return `
                    <tr>
                        <td>${student.id}</td>
                        <td>${escapeHTML(student.student_id)}</td>
                        <td>${escapeHTML(student.name)}</td>
                        <td>${escapeHTML(student.program)}</td>
                        <td>${student.year}</td>
                        <td>${escapeHTML(student.section)}</td>
                        <td>
                            <button
                                type="button"
                                class="edit"
                                onclick="editStudent(${student.id})">
                                Edit
                            </button>

                            <button
                                type="button"
                                class="delete"
                                onclick="deleteStudent(${student.id})">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            }).join("");

        } catch (error) {
            table.innerHTML =
                '<tr><td colspan="7">Unable to load student records.</td></tr>';

            showMessage(error.message, "error");
        }
    }

    // CREATE OR UPDATE STUDENT
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const recordId = document.getElementById("recordId").value;

        const student = {
            student_id: document.getElementById("student_id").value.trim(),
            name: document.getElementById("name").value.trim(),
            program: document.getElementById("program").value,
            year: Number(document.getElementById("year").value),
            section: document.getElementById("section").value
        };

        const url = recordId
            ? `/api/students/${recordId}`
            : "/api/students";

        const method = recordId ? "PUT" : "POST";

        const saveButton = document.getElementById("saveButton");
        saveButton.disabled = true;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(student)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Unable to save student.");
            }

            showMessage(
                recordId
                    ? "Student updated successfully!"
                    : "Student created successfully!",
                "success"
            );

            resetForm();
            await loadStudents();

        } catch (error) {
            showMessage(error.message, "error");
        } finally {
            saveButton.disabled = false;
        }
    });

    // EDIT: LOAD EXISTING STUDENT DETAILS INTO THE FORM
    async function editStudent(id) {
        try {
            const response = await fetch(`/api/students/${id}`);
            const student = await response.json();

            if (!response.ok) {
                throw new Error(student.error || "Student not found.");
            }

            document.getElementById("recordId").value = student.id;
            document.getElementById("student_id").value = student.student_id;
            document.getElementById("name").value = student.name;
            document.getElementById("program").value = student.program;
            document.getElementById("year").value = String(student.year);
            document.getElementById("section").value = student.section;

            document.getElementById("formTitle").textContent = "Edit Student";
            document.getElementById("saveButton").textContent = "Update Student";
            document.getElementById("cancelButton").hidden = false;

            showMessage(
                "Edit the information, then click Update Student.",
                "success"
            );

            document.getElementById("studentForm").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            showMessage(error.message, "error");
        }
    }

    // RESET FORM / CANCEL EDIT
    function resetForm() {
        form.reset();

        document.getElementById("recordId").value = "";
        document.getElementById("formTitle").textContent = "Add Student";
        document.getElementById("saveButton").textContent = "Save Student";
        document.getElementById("cancelButton").hidden = true;
    }

    document.getElementById("cancelButton").addEventListener(
        "click",
        function() {
            resetForm();
            showMessage("Edit cancelled.", "success");
        }
    );

    // DELETE STUDENT
    async function deleteStudent(id) {
        if (!confirm("Are you sure you want to delete this student?")) {
            return;
        }

        try {
            const response = await fetch(`/api/students/${id}`, {
                method: "DELETE"
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Unable to delete student.");
            }

            showMessage(result.message, "success");

            if (document.getElementById("recordId").value === String(id)) {
                resetForm();
            }

            await loadStudents();

        } catch (error) {
            showMessage(error.message, "error");
        }
    }

    // RETRIEVE CLASSMATE API RECORDS
    async function loadClassmateStudents() {
        const output = document.getElementById("classmateOutput");
        output.textContent = "Loading classmate records...";

        try {
            const response = await fetch("/api/classmate/students");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to retrieve records.");
            }

            output.textContent = JSON.stringify(data, null, 2);

        } catch (error) {
            output.textContent = error.message;
        }
    }

    document.getElementById("refreshButton").addEventListener(
        "click", loadStudents
    );

    document.getElementById("classmateButton").addEventListener(
        "click", loadClassmateStudents
    );

    // LOAD RECORDS WHEN THE PAGE OPENS
    loadStudents();
</script>

</body>
</html>
""")


# ==========================================
# API INFORMATION
# ==========================================
@app.route("/api")
def api_info():
    return jsonify({
        "message": "Student Information API",
        "endpoints": {
            "all_students": "GET /api/students",
            "create_student": "POST /api/students",
            "read_student": "GET /api/students/<id>",
            "update_student": "PUT /api/students/<id>",
            "delete_student": "DELETE /api/students/<id>",
            "classmate_students": "GET /api/classmate/students"
        }
    })


# ==========================================
# READ ALL STUDENTS / CREATE STUDENT
# ==========================================
@app.route("/api/students", methods=["GET", "POST"])
def students():

    if request.method == "GET":
        try:
            with get_db_connection() as conn:
                records = conn.execute(
                    "SELECT * FROM students ORDER BY id"
                ).fetchall()

            return jsonify([student_to_dict(row) for row in records])

        except sqlite3.Error:
            app.logger.exception("Unable to read students")
            return jsonify({"error": "Database error."}), 500

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Provide a valid JSON object."}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if any(
        key not in data or data[key] is None
        or str(data[key]).strip() == ""
        for key in required
    ):
        return jsonify({"error": "All fields are required."}), 400

    try:
        year = int(data["year"])

        if not 1 <= year <= 6:
            return jsonify({
                "error": "Year must be between 1 and 6."
            }), 400

        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO students
                (student_id, name, program, year, section)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                year,
                str(data["section"]).strip().upper()
            ))

            record = conn.execute(
                "SELECT * FROM students WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

        return jsonify(student_to_dict(record)), 201

    except ValueError:
        return jsonify({"error": "Year must be a number."}), 400

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists."}), 409

    except sqlite3.Error:
        app.logger.exception("Unable to create student")
        return jsonify({"error": "Database error."}), 500


# ==========================================
# READ ONE / UPDATE / DELETE STUDENT
# ==========================================
@app.route(
    "/api/students/<int:student_id>",
    methods=["GET", "PUT", "DELETE"]
)
def student_detail(student_id):

    # READ ONE
    if request.method == "GET":
        try:
            with get_db_connection() as conn:
                student = conn.execute(
                    "SELECT * FROM students WHERE id = ?",
                    (student_id,)
                ).fetchone()

            if student is None:
                return jsonify({"error": "Student not found."}), 404

            return jsonify(student_to_dict(student))

        except sqlite3.Error:
            app.logger.exception("Unable to read student")
            return jsonify({"error": "Database error."}), 500

    # UPDATE
    if request.method == "PUT":
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Provide a valid JSON object."}), 400

        required = ["student_id", "name", "program", "year", "section"]

        if any(
            key not in data or data[key] is None
            or str(data[key]).strip() == ""
            for key in required
        ):
            return jsonify({"error": "All fields are required."}), 400

        try:
            year = int(data["year"])

            if not 1 <= year <= 6:
                return jsonify({
                    "error": "Year must be between 1 and 6."
                }), 400

            with get_db_connection() as conn:
                existing = conn.execute(
                    "SELECT id FROM students WHERE id = ?",
                    (student_id,)
                ).fetchone()

                if existing is None:
                    return jsonify({"error": "Student not found."}), 404

                conn.execute("""
                    UPDATE students
                    SET student_id = ?,
                        name = ?,
                        program = ?,
                        year = ?,
                        section = ?
                    WHERE id = ?
                """, (
                    str(data["student_id"]).strip(),
                    str(data["name"]).strip(),
                    str(data["program"]).strip(),
                    year,
                    str(data["section"]).strip().upper(),
                    student_id
                ))

                updated = conn.execute(
                    "SELECT * FROM students WHERE id = ?",
                    (student_id,)
                ).fetchone()

            return jsonify(student_to_dict(updated))

        except ValueError:
            return jsonify({"error": "Year must be a number."}), 400

        except sqlite3.IntegrityError:
            return jsonify({"error": "Student ID already exists."}), 409

        except sqlite3.Error:
            app.logger.exception("Unable to update student")
            return jsonify({"error": "Database error."}), 500

    # DELETE
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,)
            )

            deleted = cursor.rowcount

        if deleted == 0:
            return jsonify({"error": "Student not found."}), 404

        return jsonify({"message": "Student deleted successfully."})

    except sqlite3.Error:
        app.logger.exception("Unable to delete student")
        return jsonify({"error": "Database error."}), 500


# ==========================================
# CLASSMATE API
# ==========================================
@app.route("/api/classmate/students")
def classmate_students():
    try:
        response = requests.get(
            f"{CLASSMATE_API_URL}/api/students",
            timeout=45
        )
        response.raise_for_status()

        return jsonify(response.json())

    except requests.RequestException:
        app.logger.exception("Classmate API request failed")
        return jsonify({
            "error": "Unable to retrieve classmate API records."
        }), 502

    except ValueError:
        return jsonify({
            "error": "Classmate API returned invalid JSON."
        }), 502


# ==========================================
# LOCAL DEVELOPMENT SERVER
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
