
from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import sqlite3
import os
import requests

app = Flask(__name__)

DATABASE = "students.db"

# Classmate's deployed API
PARTNER_API_URL = "https://jasminerose-2.onrender.com/api/students"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    cursor.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    if "source" not in columns:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN source TEXT DEFAULT 'Local'
        """)

    cursor.execute("""
        UPDATE students
        SET source = 'Local'
        WHERE source IS NULL OR source = ''
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "2026-00123",
        "Arnie Beliran",
        "BSIT",
        3,
        "A",
        "Local"
    ))

    conn.commit()
    conn.close()


# ==================================================
# SHARED HTML DESIGN
# ==================================================

STYLE = """
<style>
    * {
        box-sizing: border-box;
    }

    body {
        font-family: Arial, sans-serif;
        background: #f1f5f9;
        color: #1e293b;
        margin: 0;
        padding: 24px;
    }

    .container {
        max-width: 1100px;
        margin: 0 auto;
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    }

    h1, h2 {
        color: #164e9b;
    }

    .button {
        display: inline-block;
        background: #164e9b;
        color: white;
        padding: 10px 14px;
        margin: 4px 3px;
        text-decoration: none;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
    }

    .button:hover {
        background: #0f3973;
    }

    .danger {
        background: #b91c1c;
    }

    .success {
        background: #15803d;
    }

    .secondary {
        background: #475569;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 18px;
        background: white;
    }

    th, td {
        border: 1px solid #dbe2ea;
        padding: 10px;
        text-align: left;
    }

    th {
        background: #164e9b;
        color: white;
    }

    input, select {
        width: 100%;
        padding: 10px;
        margin: 6px 0 14px;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
    }

    label {
        font-weight: bold;
    }

    .card {
        background: #f8fafc;
        border: 1px solid #dbe2ea;
        padding: 18px;
        border-radius: 8px;
        margin: 12px 0;
    }

    .message {
        padding: 12px;
        background: #e0f2fe;
        border-radius: 6px;
        margin: 12px 0;
    }

    pre {
        background: #0f172a;
        color: #e2e8f0;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
    }

    @media (max-width: 700px) {
        body {
            padding: 10px;
        }

        .container {
            padding: 12px;
            overflow-x: auto;
        }

        table {
            min-width: 650px;
        }
    }
</style>
"""


# ==================================================
# HOME DASHBOARD
# ==================================================

@app.route("/")
def home():
    conn = get_db_connection()
    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    local_students = conn.execute(
        "SELECT COUNT(*) FROM students WHERE source = 'Local'"
    ).fetchone()[0]

    partner_students = conn.execute(
        "SELECT COUNT(*) FROM students WHERE source = 'Classmate API'"
    ).fetchone()[0]

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Information System</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="container">
            <h1>Student Information System</h1>
            <p><strong>Developer:</strong> Arnie Beliran</p>
            <p>Flask API with SQLite and System-to-System Integration</p>

            <div class="card">
                <h2>Dashboard Summary</h2>
                <p>Total student records: <strong>{{ total }}</strong></p>
                <p>Local records: <strong>{{ local }}</strong></p>
                <p>Imported classmate records:
                    <strong>{{ partner }}</strong>
                </p>
            </div>

            <h2>Student Management</h2>
            <a class="button" href="/students">View Students</a>
            <a class="button" href="/students/add">Add Student</a>

            <h2>API and Integration</h2>
            <a class="button" href="/api">View API Endpoints</a>
            <a class="button" href="/api/students">View JSON API</a>
            <a class="button" href="/partner-records">View Partner API</a>
            <a class="button" href="/integration">Integration Dashboard</a>
        </div>
    </body>
    </html>
    """,
    style=STYLE,
    total=total_students,
    local=local_students,
    partner=partner_students)


# ==================================================
# API ENDPOINT DOCUMENTATION
# GET /api
# ==================================================

@app.route("/api", methods=["GET"])
def api_documentation():
    endpoints = [
        {
            "method": "GET",
            "endpoint": "/api",
            "description": "View the list of API endpoints"
        },
        {
            "method": "GET",
            "endpoint": "/api/students",
            "description": "Retrieve all student records in JSON"
        },
        {
            "method": "POST",
            "endpoint": "/api/students",
            "description": "Create a student record using JSON"
        },
        {
            "method": "GET",
            "endpoint": "/students",
            "description": "View student records in the web interface"
        },
        {
            "method": "GET",
            "endpoint": "/students/add",
            "description": "Open the add-student form"
        },
        {
            "method": "GET",
            "endpoint": "/partner-records",
            "description": "Retrieve records from the classmate API"
        },
        {
            "method": "GET",
            "endpoint": "/integration",
            "description": "Open the integration dashboard"
        },
        {
            "method": "POST",
            "endpoint": "/import-student",
            "description": "Import a selected partner record"
        },
        {
            "method": "GET",
            "endpoint": "/students/edit/<id>",
            "description": "Open the edit form for a student"
        },
        {
            "method": "POST",
            "endpoint": "/students/edit/<id>",
            "description": "Update a student record"
        },
        {
            "method": "POST",
            "endpoint": "/students/delete/<id>",
            "description": "Delete a student record"
        }
    ]

    return jsonify({
        "application": "Student Information API",
        "developer": "Arnie Beliran",
        "database": "SQLite",
        "partner_api": PARTNER_API_URL,
        "endpoints": endpoints
    })


# ==================================================
# STUDENT API
# GET /api/students
# POST /api/students
# ==================================================

@app.route("/api/students", methods=["GET", "POST"])
def students_api():
    if request.method == "GET":
        conn = get_db_connection()
        rows = conn.execute("""
            SELECT id, student_id, name, program, year, section, source
            FROM students
            ORDER BY id
        """).fetchall()
        conn.close()

        return jsonify({
            "count": len(rows),
            "students": [dict(row) for row in rows]
        }), 200

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON."
        }), 400

    required_fields = [
        "student_id", "name", "program", "year", "section"
    ]

    missing = [
        field for field in required_fields
        if field not in data
        or data[field] is None
        or str(data[field]).strip() == ""
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing
        }), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number."}), 400

    if year < 1 or year > 6:
        return jsonify({
            "error": "Year must be between 1 and 6."
        }), 400

    student = {
        "student_id": str(data["student_id"]).strip(),
        "name": str(data["name"]).strip(),
        "program": str(data["program"]).strip(),
        "year": year,
        "section": str(data["section"]).strip().upper(),
        "source": "External API"
    }

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student["student_id"],
            student["name"],
            student["program"],
            student["year"],
            student["section"],
            student["source"]
        ))

        conn.commit()
        student["id"] = cursor.lastrowid

        return jsonify({
            "message": "Student created successfully.",
            "student": student
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    finally:
        conn.close()


# ==================================================
# VIEW ALL STUDENTS
# ==================================================

@app.route("/students")
def view_students():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM students ORDER BY id
    """).fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Records</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="container">
            <h1>Student Records</h1>
            <a class="button" href="/">Home</a>
            <a class="button" href="/students/add">Add Student</a>
            <a class="button" href="/integration">Integration Dashboard</a>

            {% if rows %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Program</th>
                        <th>Year</th>
                        <th>Section</th>
                        <th>Source</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td>{{ row["id"] }}</td>
                        <td>{{ row["student_id"] }}</td>
                        <td>{{ row["name"] }}</td>
                        <td>{{ row["program"] }}</td>
                        <td>{{ row["year"] }}</td>
                        <td>{{ row["section"] }}</td>
                        <td>{{ row["source"] }}</td>
                        <td>
                            <a class="button"
                               href="/students/edit/{{ row['id'] }}">
                               Edit
                            </a>
                            <form method="POST"
                                  action="/students/delete/{{ row['id'] }}"
                                  onsubmit="return confirm('Delete this record?');">
                                <button class="button danger" type="submit">
                                    Delete
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No student records found.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """, style=STYLE, rows=rows)


# ==================================================
# ADD STUDENT FORM
# ==================================================

@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    error = None

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        program = request.form.get("program", "").strip()
        year_text = request.form.get("year", "").strip()
        section = request.form.get("section", "").strip().upper()

        try:
            year = int(year_text)
            if year < 1 or year > 6:
                raise ValueError
        except ValueError:
            error = "Year must be a number between 1 and 6."

        if not all([student_id, name, program, section]):
            error = "Please complete all required fields."

        if not error:
            conn = get_db_connection()

            try:
                conn.execute("""
                    INSERT INTO students
                    (student_id, name, program, year, section, source)
                    VALUES (?, ?, ?, ?, ?, 'Local')
                """, (student_id, name, program, year, section))

                conn.commit()
                conn.close()
                return redirect(url_for("view_students"))

            except sqlite3.IntegrityError:
                error = "That Student ID already exists."
                conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Student</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="container">
            <h1>Add Student</h1>
            <a class="button secondary" href="/">Home</a>
            <a class="button secondary" href="/students">Back to Students</a>

            {% if error %}
            <div class="message">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <label>Student ID</label>
                <input name="student_id" required>

                <label>Full Name</label>
                <input name="name" required>

                <label>Program</label>
                <input name="program" placeholder="BSIT" required>

                <label>Year</label>
                <input type="number" name="year" min="1" max="6" required>

                <label>Section</label>
                <input name="section" required>

                <button class="button success" type="submit">
                    Save Student
                </button>
            </form>
        </div>
    </body>
    </html>
    """, style=STYLE, error=error)


# ==================================================
# EDIT STUDENT
# ==================================================

@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if student is None:
        conn.close()
        return jsonify({"error": "Student not found."}), 404

    error = None

    if request.method == "POST":
        new_student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        program = request.form.get("program", "").strip()
        year_text = request.form.get("year", "").strip()
        section = request.form.get("section", "").strip().upper()

        try:
            year = int(year_text)
            if year < 1 or year > 6:
                raise ValueError
        except ValueError:
            error = "Year must be a number between 1 and 6."

        if not all([new_student_id, name, program, section]):
            error = "Please complete all required fields."

        if not error:
            try:
                conn.execute("""
                    UPDATE students
                    SET student_id = ?, name = ?, program = ?,
                        year = ?, section = ?
                    WHERE id = ?
                """, (
                    new_student_id, name, program,
                    year, section, student_id
                ))

                conn.commit()
                conn.close()
                return redirect(url_for("view_students"))

            except sqlite3.IntegrityError:
                error = "That Student ID is already being used."

        student = {
            "id": student_id,
            "student_id": new_student_id,
            "name": name,
            "program": program,
            "year": year_text,
            "section": section,
            "source": student["source"]
        }

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Student</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="container">
            <h1>Edit Student</h1>
            <a class="button secondary" href="/students">Back to Students</a>

            {% if error %}
            <div class="message">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <label>Student ID</label>
                <input name="student_id"
                       value="{{ student['student_id'] }}" required>

                <label>Full Name</label>
                <input name="name" value="{{ student['name'] }}" required>

                <label>Program</label>
                <input name="program"
                       value="{{ student['program'] }}" required>

                <label>Year</label>
                <input type="number" name="year" min="1" max="6"
                       value="{{ student['year'] }}" required>

                <label>Section</label>
                <input name="section"
                       value="{{ student['section'] }}" required>

                <button class="button success" type="submit">
                    Update Student
                </button>
            </form>
        </div>
    </body>
    </html>
    """, style=STYLE, student=student, error=error)


# ==================================================
# DELETE STUDENT
# ==================================================

@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("view_students"))


# ==================================================
# FETCH RECORDS FROM CLASSMATE API
# GET /partner-records
# ==================================================

@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        response = requests.get(PARTNER_API_URL, timeout=30)
        response.raise_for_status()
        partner_data = response.json()

        return jsonify({
            "message": "Partner API data retrieved successfully.",
            "partner_api": PARTNER_API_URL,
            "partner_data": partner_data
        }), 200

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to connect to the classmate API.",
            "details": str(error),
            "partner_api": PARTNER_API_URL
        }), 502

    except ValueError:
        return jsonify({
            "error": "The partner API did not return valid JSON."
        }), 502


# ==================================================
# IMPORT ONE PARTNER RECORD INTO LOCAL DATABASE
# POST /import-student
# ==================================================

@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A student record in JSON format is required."
        }), 400

    required_fields = [
        "student_id", "name", "program", "year", "section"
    ]

    missing = [
        field for field in required_fields
        if field not in data
        or data[field] is None
        or str(data[field]).strip() == ""
    ]

    if missing:
        return jsonify({
            "error": "The partner record is missing required fields.",
            "missing_fields": missing
        }), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number."}), 400

    if year < 1 or year > 6:
        return jsonify({
            "error": "Year must be between 1 and 6."
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, 'Classmate API')
        """, (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            year,
            str(data["section"]).strip().upper()
        ))

        conn.commit()

        return jsonify({
            "message": "Partner student imported successfully.",
            "local_record_id": cursor.lastrowid,
            "student_id": str(data["student_id"]).strip(),
            "source": "Classmate API"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This Student ID already exists in your database."
        }), 409

    finally:
        conn.close()


# ==================================================
# INTEGRATION DASHBOARD
# ==================================================

@app.route("/integration")
def integration_dashboard():
    try:
        response = requests.get(PARTNER_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Accept either a JSON list or common dictionary formats.
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get(
                "students",
                data.get("data", data.get("records", []))
            )
        else:
            records = []

        if not isinstance(records, list):
            records = []

        # Convert records to a consistent format for the page.
        normalized_records = []

        for record in records:
            if not isinstance(record, dict):
                continue

            normalized_records.append({
                "student_id": record.get(
                    "student_id", record.get("id_number", record.get("id", ""))
                ),
                "name": record.get(
                    "name",
                    " ".join(filter(None, [
                        record.get("first_name", ""),
                        record.get("middle_name", ""),
                        record.get("last_name", "")
                    ])).strip()
                ),
                "program": record.get(
                    "program", record.get("course", "")
                ),
                "year": record.get("year", 1),
                "section": record.get("section", "A")
            })

        error = None

    except (requests.RequestException, ValueError) as exc:
        normalized_records = []
        error = str(exc)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Integration</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="container">
            <h1>System-to-System Integration</h1>
            <p>View records from your classmate's API and import a selected
               record into your local SQLite database.</p>

            <a class="button secondary" href="/">Home</a>
            <a class="button" href="/students">My Student Records</a>
            <a class="button" href="/partner-records">Partner JSON</a>

            {% if error %}
            <div class="message">
                Could not retrieve partner records: {{ error }}
                <p>Check that the partner API URL is correct and that the
                   classmate's service is running.</p>
            </div>
            {% elif records %}
            <h2>Partner Records</h2>
            <table>
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Program</th>
                        <th>Year</th>
                        <th>Section</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for record in records %}
                    <tr>
                        <td>{{ record["student_id"] }}</td>
                        <td>{{ record["name"] }}</td>
                        <td>{{ record["program"] }}</td>
                        <td>{{ record["year"] }}</td>
                        <td>{{ record["section"] }}</td>
                        <td>
                            <button class="button"
                                type="button"
                                onclick='selectRecord({{ record|tojson }})'>
                                View / Select
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="card">
                <h2>Selected Partner Record</h2>
                <pre id="selectedRecord">Select a record from the table.</pre>
                <button class="button success" id="saveButton"
                        type="button" disabled onclick="saveRecord()">
                    Save to My Database
                </button>
                <p id="result"></p>
            </div>
            {% else %}
            <div class="message">
                The partner API returned no records, or its JSON response
                did not contain a supported student list.
            </div>
            {% endif %}
        </div>

        <script>
            let selectedStudent = null;

            function selectRecord(record) {
                selectedStudent = record;
                document.getElementById("selectedRecord").textContent =
                    JSON.stringify(record, null, 2);

                document.getElementById("saveButton").disabled = false;
                document.getElementById("result").textContent = "";
            }

            async function saveRecord() {
                if (!selectedStudent) {
                    return;
                }

                const result = document.getElementById("result");
                const button = document.getElementById("saveButton");

                button.disabled = true;
                result.textContent = "Saving record...";

                try {
                    const response = await fetch("/import-student", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(selectedStudent)
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        result.textContent =
                            data.error || "Could not save the record.";
                    } else {
                        result.textContent =
                            data.message + " Source: " + data.source + ".";
                    }
                } catch (error) {
                    result.textContent = "Request failed: " + error.message;
                } finally {
                    button.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """, style=STYLE, records=normalized_records, error=error)


# ==================================================
# START APPLICATION
# ==================================================

initialize_database()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
