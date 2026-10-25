
from flask import (
    Flask, jsonify, render_template_string,
    request, redirect, url_for
)
import sqlite3
import os
import requests

app = Flask(__name__)

DATABASE = "students.db"

# Replace this if your classmate gives you another API URL.
PARTNER_API_URL = "https://jasminerose-2.onrender.com/api/students"


# ==================================================
# DATABASE
# ==================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    ]

    if "source" not in columns:
        conn.execute("""
            ALTER TABLE students
            ADD COLUMN source TEXT DEFAULT 'Local'
        """)

    conn.execute("""
        UPDATE students
        SET source = 'Local'
        WHERE source IS NULL OR source = ''
    """)

    conn.execute("""
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
# SHARED CSS
# ==================================================

STYLE = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #1e293b;
}

header {
    background: #164e9b;
    color: white;
    text-align: center;
    padding: 25px 15px;
}

header h1 {
    margin: 0 0 8px;
}

header p {
    margin: 0;
}

.container {
    width: 92%;
    max-width: 1100px;
    margin: 30px auto;
}

.card {
    background: white;
    padding: 25px;
    margin-bottom: 22px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
}

h2 {
    color: #164e9b;
    margin-top: 0;
}

p {
    line-height: 1.6;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.info-item {
    background: #eff6ff;
    padding: 15px;
    border-radius: 8px;
}

.info-item strong {
    display: block;
    color: #164e9b;
    margin-bottom: 6px;
}

.button, button {
    display: inline-block;
    border: none;
    border-radius: 6px;
    padding: 11px 16px;
    margin: 4px 3px 4px 0;
    background: #164e9b;
    color: white;
    text-decoration: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
}

.button:hover, button:hover {
    background: #0f3670;
}

.green {
    background: #0f766e;
}

.green:hover {
    background: #115e59;
}

.orange {
    background: #c77712;
}

.orange:hover {
    background: #9a5a0d;
}

.red {
    background: #dc2626;
}

.red:hover {
    background: #b91c1c;
}

.table-wrapper {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background: white;
}

th, td {
    padding: 12px 10px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

th {
    background: #164e9b;
    color: white;
}

tr:hover td {
    background: #eff6ff;
}

label {
    display: block;
    font-weight: bold;
    margin-top: 12px;
}

input, select {
    display: block;
    width: 100%;
    padding: 11px;
    margin: 7px 0 14px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 15px;
}

footer {
    text-align: center;
    color: #64748b;
    padding: 22px;
}

pre {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: #f1f5f9;
    padding: 15px;
    border-radius: 8px;
}

@media (max-width: 600px) {
    .info-grid {
        grid-template-columns: 1fr;
    }

    .card {
        padding: 18px;
    }
}
</style>
"""


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>Student Information API</title>
        {{ style | safe }}
    </head>
    <body>
        <header>
            <h1>Student Information API</h1>
            <p>Flask and SQLite Database System</p>
        </header>

        <main class="container">
            <section class="card">
                <h2>Welcome to the Student Information System</h2>
                <p>
                    Manage your student records and exchange practice
                    records with your classmate through REST APIs.
                </p>

                <a class="button" href="/api/students">
                    View Students JSON
                </a>

                <a class="button green" href="/students">
                    My Records
                </a>

                <a class="button orange" href="/students/add">
                    Add Student
                </a>

                <a class="button" href="/integration">
                    Integration Dashboard
                </a>
            </section>

            <section class="card">
                <h2>Developer Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Developer</strong>
                        Arnie Beliran
                    </div>
                    <div class="info-item">
                        <strong>Technology</strong>
                        Python Flask
                    </div>
                    <div class="info-item">
                        <strong>Database</strong>
                        SQLite
                    </div>
                    <div class="info-item">
                        <strong>API Endpoint</strong>
                        /api/students
                    </div>
                </div>
            </section>
        </main>

        <footer>Student Information API &copy; 2026</footer>
    </body>
    </html>
    """, style=STYLE)


# ==================================================
# CREATE AND READ JSON API
# GET /api/students
# POST /api/students
# ==================================================

@app.route("/api/students", methods=["GET", "POST"])
def students_api():

    # READ: return all local records as JSON.
    if request.method == "GET":
        conn = get_db_connection()

        students = conn.execute("""
            SELECT id, student_id, name, program, year, section, source
            FROM students
            ORDER BY id
        """).fetchall()

        conn.close()

        return jsonify([dict(student) for student in students])

    # CREATE: receive a record from a client or partner.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send a JSON student record."
        }), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(
        field not in data or str(data[field]).strip() == ""
        for field in required
    ):
        return jsonify({
            "error": "All student fields are required."
        }), 400

    try:
        year = int(data["year"])

        if year < 1 or year > 6:
            return jsonify({
                "error": "Year must be between 1 and 6."
            }), 400

        source = str(data.get("source", "External API")).strip()

        if not source:
            source = "External API"

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            year,
            str(data["section"]).strip().upper(),
            source
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student record created successfully.",
            "student_id": data["student_id"],
            "source": source
        }), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "error": "This student ID already exists."
        }), 409

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid year value."
        }), 400


# ==================================================
# CREATE: HTML ADD FORM
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

        if not all([student_id, name, program, year_text, section]):
            error = "Please complete all fields."
        else:
            try:
                year = int(year_text)

                if year < 1 or year > 6:
                    error = "Year must be between 1 and 6."
                else:
                    conn = get_db_connection()

                    conn.execute("""
                        INSERT INTO students
                        (student_id, name, program, year, section, source)
                        VALUES (?, ?, ?, ?, ?, 'Local')
                    """, (
                        student_id, name, program, year, section
                    ))

                    conn.commit()
                    conn.close()

                    return redirect(url_for("student_table"))

            except sqlite3.IntegrityError:
                error = "That student ID already exists."
            except ValueError:
                error = "Year must be a valid number."

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Add Student</title>
        {{ style | safe }}
    </head>
    <body>
        <header><h1>Add Student</h1></header>
        <main class="container">
            <section class="card">
                <h2>Student Information</h2>
                {% if error %}
                    <p style="color:#dc2626">{{ error }}</p>
                {% endif %}

                <form method="POST">
                    <label>Student ID</label>
                    <input name="student_id" required>

                    <label>Full Name</label>
                    <input name="name" required>

                    <label>Program</label>
                    <input name="program" value="BSIT" required>

                    <label>Year</label>
                    <input name="year" type="number"
                           min="1" max="6" required>

                    <label>Section</label>
                    <input name="section" required>

                    <button class="green" type="submit">
                        Save Student
                    </button>
                    <a class="button" href="/students">Cancel</a>
                </form>
            </section>
        </main>
    </body>
    </html>
    """, style=STYLE, error=error)


# ==================================================
# READ: HTML TABLE WITH SOURCE
# ==================================================

@app.route("/students")
def student_table():
    conn = get_db_connection()

    students = conn.execute("""
        SELECT id, student_id, name, program, year, section, source
        FROM students
        ORDER BY id
    """).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>My Student Records</title>
        {{ style | safe }}
    </head>
    <body>
        <header>
            <h1>My Student Records</h1>
            <p>Local and imported database records</p>
        </header>

        <main class="container">
            <section class="card">
                <a class="button green" href="/students/add">Add Student</a>
                <a class="button" href="/api/students">View JSON</a>
                <a class="button orange" href="/integration">
                    Integration Dashboard
                </a>
                <a class="button" href="/">Home</a>

                <div class="table-wrapper">
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
                        {% for s in students %}
                            <tr>
                                <td>{{ s['id'] }}</td>
                                <td>{{ s['student_id'] }}</td>
                                <td>{{ s['name'] }}</td>
                                <td>{{ s['program'] }}</td>
                                <td>{{ s['year'] }}</td>
                                <td>{{ s['section'] }}</td>
                                <td>{{ s['source'] }}</td>
                                <td>
                                    <a class="button orange"
                                       href="/students/edit/{{ s['id'] }}">
                                       Edit
                                    </a>

                                    <form method="POST"
                                          action="/students/delete/{{ s['id'] }}"
                                          style="display:inline"
                                          onsubmit="return confirm(
                                            'Delete this record?'
                                          )">
                                        <button class="red" type="submit">
                                            Delete
                                        </button>
                                    </form>
                                </td>
                            </tr>
                        {% else %}
                            <tr>
                                <td colspan="8">No records found.</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </body>
    </html>
    """, style=STYLE, students=students)


# ==================================================
# UPDATE: EDIT STUDENT
# ==================================================

@app.route("/students/edit/<int:student_id>",
           methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found.", 404

    error = None

    if request.method == "POST":
        new_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        program = request.form.get("program", "").strip()
        year_text = request.form.get("year", "").strip()
        section = request.form.get("section", "").strip().upper()

        if not all([new_id, name, program, year_text, section]):
            error = "Please complete all fields."
        else:
            try:
                year = int(year_text)

                if year < 1 or year > 6:
                    error = "Year must be between 1 and 6."
                else:
                    conn = get_db_connection()

                    conn.execute("""
                        UPDATE students
                        SET student_id = ?, name = ?, program = ?,
                            year = ?, section = ?
                        WHERE id = ?
                    """, (
                        new_id, name, program, year, section, student_id
                    ))

                    conn.commit()
                    conn.close()

                    return redirect(url_for("student_table"))

            except sqlite3.IntegrityError:
                error = "That student ID already exists."
            except ValueError:
                error = "Year must be a valid number."

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Edit Student</title>
        {{ style | safe }}
    </head>
    <body>
        <header><h1>Update Student Record</h1></header>
        <main class="container">
            <section class="card">
                {% if error %}
                    <p style="color:#dc2626">{{ error }}</p>
                {% endif %}

                <form method="POST">
                    <label>Student ID</label>
                    <input name="student_id"
                           value="{{ request.form.get(
                               'student_id', student['student_id']
                           ) }}" required>

                    <label>Full Name</label>
                    <input name="name"
                           value="{{ request.form.get(
                               'name', student['name']
                           ) }}" required>

                    <label>Program</label>
                    <input name="program"
                           value="{{ request.form.get(
                               'program', student['program']
                           ) }}" required>

                    <label>Year</label>
                    <input name="year" type="number" min="1" max="6"
                           value="{{ request.form.get(
                               'year', student['year']
                           ) }}" required>

                    <label>Section</label>
                    <input name="section"
                           value="{{ request.form.get(
                               'section', student['section']
                           ) }}" required>

                    <button class="green" type="submit">
                        Update Student
                    </button>
                    <a class="button" href="/students">Cancel</a>
                </form>
            </section>
        </main>
    </body>
    </html>
    """, style=STYLE, student=student, error=error)


# ==================================================
# DELETE: REMOVE STUDENT
# ==================================================

@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("student_table"))


# ==================================================
# RETRIEVE CLASSMATE RECORDS
# ==================================================

@app.route("/partner-records")
def partner_records():
    try:
        response = requests.get(PARTNER_API_URL, timeout=15)
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "Partner API did not return a list."
            }), 502

        return jsonify(records)

    except (requests.RequestException, ValueError):
        return jsonify({
            "error": "Unable to retrieve partner data. Check the partner URL and API."
        }), 502


# ==================================================
# IMPORT A SELECTED CLASSMATE RECORD
# ==================================================

@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON record is required."}), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(
        field not in data or str(data[field]).strip() == ""
        for field in required
    ):
        return jsonify({"error": "Missing required student fields."}), 400

    try:
        year = int(data["year"])

        if year < 1 or year > 6:
            return jsonify({"error": "Year must be between 1 and 6."}), 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            year,
            str(data["section"]).strip().upper(),
            "Classmate API"
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Remote record saved successfully.",
            "source": "Classmate API"
        }), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "error": "This student ID already exists in your database."
        }), 409

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year value."}), 400


# ==================================================
# INTEGRATION DASHBOARD
# ==================================================

@app.route("/integration")
def integration_dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Integration Dashboard</title>
        {{ style | safe }}
    </head>
    <body>
        <header>
            <h1>Integration Dashboard</h1>
            <p>View, save, send, and retrieve student records</p>
        </header>

        <main class="container">
            <section class="card">
                <h2>My Local Records and Imported Records</h2>
                <p>View saved records and check their source.</p>
                <a class="button green" href="/students">My Records</a>
                <a class="button" href="/api/students">My JSON API</a>
            </section>

            <section class="card">
                <h2>Partner Records</h2>
                <button onclick="loadPartnerRecords()">
                    Retrieve Partner Records
                </button>
                <p id="message" role="status"></p>

                <div class="table-wrapper">
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
                        <tbody id="partnerTable">
                            <tr>
                                <td colspan="6">
                                    Click Retrieve Partner Records.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section class="card">
                <h2>Selected Partner Record</h2>
                <p>Review the record before saving it locally.</p>
                <pre id="selectedRecord">No record selected.</pre>
                <button class="green" id="saveButton"
                        onclick="saveSelectedRecord()" disabled>
                    Save to My Database
                </button>
            </section>

            <section class="card">
                <h2>Send a Practice Record</h2>
                <p>
                    To send a record, use the send_to_partner.py script
                    after coordinating with your classmate.
                </p>
                <a class="button" href="/api/students">Open My API</a>
            </section>

            <a class="button" href="/">Back to Home</a>
        </main>

        <script>
            let partnerRecords = [];
            let selectedStudent = null;

            async function loadPartnerRecords() {
                const message = document.getElementById("message");
                const table = document.getElementById("partnerTable");

                message.textContent = "Loading partner records...";

                try {
                    const response = await fetch("/partner-records");
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || "Request failed.");
                    }

                    if (!Array.isArray(data)) {
                        throw new Error("Invalid partner response.");
                    }

                    partnerRecords = data;
                    selectedStudent = null;
                    document.getElementById("selectedRecord").textContent =
                        "No record selected.";
                    document.getElementById("saveButton").disabled = true;
                    table.replaceChildren();

                    if (data.length === 0) {
                        table.innerHTML =
                            '<tr><td colspan="6">No partner records found.</td></tr>';
                    }

                    data.forEach((student, index) => {
                        const row = document.createElement("tr");

                        [
                            student.student_id,
                            student.name,
                            student.program,
                            student.year,
                            student.section
                        ].forEach(value => {
                            const cell = document.createElement("td");
                            cell.textContent = value ?? "";
                            row.appendChild(cell);
                        });

                        const actionCell = document.createElement("td");
                        const viewButton = document.createElement("button");
                        viewButton.textContent = "View";
                        viewButton.onclick = () => selectRecord(index);
                        actionCell.appendChild(viewButton);
                        row.appendChild(actionCell);
                        table.appendChild(row);
                    });

                    message.textContent =
                        "Retrieved " + data.length + " partner record(s).";

                } catch (error) {
                    message.textContent = "Error: " + error.message;
                }
            }

            function selectRecord(index) {
                selectedStudent = partnerRecords[index];

                document.getElementById("selectedRecord").textContent =
                    JSON.stringify(selectedStudent, null, 2);

                document.getElementById("saveButton").disabled = false;
                document.getElementById("message").textContent =
                    "Review the selected record before saving.";
            }

            async function saveSelectedRecord() {
                if (!selectedStudent) return;

                const button = document.getElementById("saveButton");
                const message = document.getElementById("message");

                button.disabled = true;
                message.textContent = "Saving record...";

                try {
                    const response = await fetch("/import-student", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(selectedStudent)
                    });

                    const result = await response.json();

                    if (!response.ok) {
                        throw new Error(result.error || "Save failed.");
                    }

                    message.textContent =
                        result.message + " Source: " + result.source + ".";

                } catch (error) {
                    message.textContent = "Error: " + error.message;
                } finally {
                    button.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """, style=STYLE)


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":
    initialize_database()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
