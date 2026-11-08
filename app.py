import os
import sqlite3
import requests
from flask import Flask, render_template_string, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so your partner can read your endpoint directly from their browser
CORS(app)

DATABASE = 'students.db'

# ---------------------------------------------------------
# DATABASE SETUP & CONNECTION MANAGEMENT
# ---------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Auto-creates the table and initial seed records if the database doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('2026-0001', 'Juan Dela Cruz', 'BSIT', '3rd Year', '3A'),
            ('2026-0002', 'Maria Santos', 'BSCS', '2nd Year', '2B')
        ]
        cursor.executemany('''
            INSERT INTO students (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_students)
        conn.commit()
    conn.close()

# Initialize DB structure when server starts
init_db()

# ---------------------------------------------------------
# FRONTEND TEMPLATE (INLINE SINGLE-FILE SETUP)
# ---------------------------------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab 8: CRUD & Classmate API System</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
        body { background-color: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }
        h1 { text-align: center; color: #0f172a; margin-bottom: 24px; }
        
        .container { display: flex; gap: 24px; flex-wrap: wrap; max-width: 1400px; margin: 0 auto; }
        .card { flex: 1; min-width: 480px; background: #ffffff; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .card-title { font-size: 1.25rem; font-weight: 700; margin-top: 0; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
        
        .form-group { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
        input[type="text"], input[type="url"] { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; width: 100%; }
        input[type="text"]:focus, input[type="url"]:focus { outline: 2px solid #3b82f6; border-color: transparent; }
        
        .btn-row { display: flex; gap: 8px; }
        button { padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: background 0.2s; font-size: 14px; }
        .btn-add { background-color: #2563eb; color: #ffffff; }
        .btn-add:hover { background-color: #1d4ed8; }
        .btn-update { background-color: #d97706; color: #ffffff; }
        .btn-update:hover { background-color: #b45309; }
        .btn-cancel { background-color: #64748b; color: #ffffff; }
        .btn-cancel:hover { background-color: #475569; }
        .btn-fetch { background-color: #0d9488; color: #ffffff; }
        .btn-fetch:hover { background-color: #0f766e; }
        
        .btn-view { background-color: #0284c7; color: #ffffff; padding: 4px 10px; font-size: 12px; }
        .btn-edit { background-color: #f59e0b; color: #ffffff; padding: 4px 10px; font-size: 12px; }
        .btn-delete { background-color: #ef4444; color: #ffffff; padding: 4px 10px; font-size: 12px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #e2e8f0; }
        th { background-color: #f8fafc; font-weight: 600; color: #475569; }
        
        .details-pane { margin-top: 16px; padding: 16px; background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; font-size: 14px; }
        .details-pane h4 { margin: 0 0 8px 0; color: #0369a1; }
        .badge { background-color: #e2e8f0; color: #334155; padding: 2px 8px; border-radius: 12px; font-size: 11px; text-transform: uppercase; font-weight: 700; }
        .search-bar { margin-bottom: 12px; }
    </style>
</head>
<body>

    <h1>Laboratory Activity 8: CRUD & Distributed API System</h1>

    <div class="container">
        <!-- MY RECORDS PANEL -->
        <div class="card">
            <div class="card-title">
                <span>My Records (Local Database)</span>
                <span class="badge">SQLite</span>
            </div>

            <form id="student-form">
                <input type="hidden" id="db-id">
                <div class="form-group">
                    <input type="text" id="student_id" placeholder="Student ID (e.g., 2026-0001)" required>
                    <input type="text" id="name" placeholder="Full Name" required>
                    <input type="text" id="program" placeholder="Program (e.g., BSIT)" required>
                    <input type="text" id="year" placeholder="Year Level (e.g., 3rd Year)" required>
                    <input type="text" id="section" placeholder="Section (e.g., 3A)" required>
                </div>
                <div class="btn-row">
                    <button type="submit" id="submit-btn" class="btn-add">Add Student</button>
                    <button type="button" id="cancel-btn" class="btn-cancel" onclick="resetForm()" style="display: none;">Cancel</button>
                </div>
            </form>

            <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;">

            <input type="text" id="search-input" class="search-bar" placeholder="🔍 Search records by name or ID..." onkeyup="filterLocalRecords()">

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Program</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="local-records-body"></tbody>
            </table>

            <div id="local-details" class="details-pane" style="display: none;"></div>
        </div>

        <!-- CLASSMATE RECORDS PANEL -->
        <div class="card">
            <div class="card-title">
                <span>Classmate's Records (Remote API)</span>
                <span class="badge">Read-Only</span>
            </div>

            <div class="form-group">
                <input type="url" id="classmate-url" value="https://jasminerose-2.onrender.com/api/students" placeholder="https://jasminerose-2.onrender.com/api/students">
                <button type="button" onclick="loadClassmateData()" class="btn-fetch">Fetch Remote API</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Program</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="remote-records-body"></tbody>
            </table>

            <div id="remote-details" class="details-pane" style="display: none;"></div>
        </div>
    </div>

    <script>
        let localStudents = [];

        document.addEventListener("DOMContentLoaded", () => {
            fetchLocalRecords();
            loadClassmateData();
        });

        // --- LOCAL CRUD FUNCTIONALITY ---
        function fetchLocalRecords() {
            fetch('/api/students')
                .then(res => res.json())
                .then(data => {
                    localStudents = data;
                    renderLocalTable(localStudents);
                })
                .catch(err => console.error("Error fetching local records:", err));
        }

        function renderLocalTable(data) {
            const tbody = document.getElementById('local-records-body');
            tbody.innerHTML = '';
            if (!data.length) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">No student records found.</td></tr>';
                return;
            }
            data.forEach(s => {
                tbody.innerHTML += `
                    <tr>
                        <td>${sanitize(s.student_id)}</td>
                        <td>${sanitize(s.name)}</td>
                        <td>${sanitize(s.program)}</td>
                        <td>
                            <button onclick="viewLocalDetails(${s.id})" class="btn-view">View</button>
                            <button onclick="populateEditForm(${s.id})" class="btn-edit">Edit</button>
                            <button onclick="deleteRecord(${s.id})" class="btn-delete">Delete</button>
                        </td>
                    </tr>
                `;
            });
        }

        document.getElementById('student-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const id = document.getElementById('db-id').value;
            const payload = {
                student_id: document.getElementById('student_id').value,
                name: document.getElementById('name').value,
                program: document.getElementById('program').value,
                year: document.getElementById('year').value,
                section: document.getElementById('section').value
            };

            const method = id ? 'PUT' : 'POST';
            const url = id ? `/api/students/${id}` : '/api/students';

            fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => {
                if (!res.ok) throw new Error("HTTP error " + res.status);
                return res.json();
            })
            .then(() => {
                resetForm();
                fetchLocalRecords();
            })
            .catch(err => alert("Operation failed: " + err.message));
        });

        function populateEditForm(id) {
            const student = localStudents.find(s => s.id === id);
            if (!student) return;

            document.getElementById('db-id').value = student.id;
            document.getElementById('student_id').value = student.student_id;
            document.getElementById('name').value = student.name;
            document.getElementById('program').value = student.program;
            document.getElementById('year').value = student.year;
            document.getElementById('section').value = student.section;

            const submitBtn = document.getElementById('submit-btn');
            submitBtn.innerText = "Update Student";
            submitBtn.className = "btn-update";
            document.getElementById('cancel-btn').style.display = "inline-block";
        }

        function deleteRecord(id) {
            if (confirm("Are you sure you want to delete this record?")) {
                fetch(`/api/students/${id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(() => {
                        document.getElementById('local-details').style.display = 'none';
                        fetchLocalRecords();
                    });
            }
        }

        function resetForm() {
            document.getElementById('student-form').reset();
            document.getElementById('db-id').value = '';
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.innerText = "Add Student";
            submitBtn.className = "btn-add";
            document.getElementById('cancel-btn').style.display = "none";
        }

        function filterLocalRecords() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const filtered = localStudents.filter(s => 
                s.name.toLowerCase().includes(query) || 
                s.student_id.toLowerCase().includes(query)
            );
            renderLocalTable(filtered);
        }

        function viewLocalDetails(id) {
            const s = localStudents.find(item => item.id === id);
            if (!s) return;
            const pane = document.getElementById('local-details');
            pane.style.display = 'block';
            pane.innerHTML = `
                <h4>Local Student Details</h4>
                <div><strong>DB ID:</strong> ${s.id}</div>
                <div><strong>Student ID:</strong> ${sanitize(s.student_id)}</div>
                <div><strong>Full Name:</strong> ${sanitize(s.name)}</div>
                <div><strong>Program:</strong> ${sanitize(s.program)}</div>
                <div><strong>Year Level:</strong> ${sanitize(s.year)}</div>
                <div><strong>Section:</strong> ${sanitize(s.section)}</div>
            `;
        }

        // --- CLASSMATE REMOTE API INTEGRATION ---
        function loadClassmateData() {
            let url = document.getElementById('classmate-url').value.trim();
            if (!url) return alert("Please specify your classmate's deployed API URL.");

            if (!url.endsWith('/api/students')) {
                url = url.replace(/\/+$/, '') + '/api/students';
                document.getElementById('classmate-url').value = url;
            }

            fetch(url)
                .then(res => {
                    if (!res.ok) throw new Error("Direct CORS connection failed with status " + res.status);
                    return res.json();
                })
                .then(data => renderRemoteTable(data))
                .catch(() => {
                    fetch(`/api/proxy/classmate?url=${encodeURIComponent(url)}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.error) throw new Error(data.error);
                            renderRemoteTable(data);
                        })
                        .catch(err => alert("Failed to fetch remote API: " + err.message));
                });
        }

        function renderRemoteTable(data) {
            const tbody = document.getElementById('remote-records-body');
            tbody.innerHTML = '';

            const list = Array.isArray(data) ? data : [data];
            if (!list.length) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">No records returned by remote endpoint.</td></tr>';
                return;
            }

            list.forEach((s, idx) => {
                window[`remote_record_${idx}`] = s;
                tbody.innerHTML += `
                    <tr>
                        <td>${sanitize(s.student_id || s.id || 'N/A')}</td>
                        <td>${sanitize(s.name || 'N/A')}</td>
                        <td>${sanitize(s.program || 'N/A')}</td>
                        <td>
                            <button onclick="viewRemoteDetails(${idx})" class="btn-view">View Details</button>
                        </td>
                    </tr>
                `;
            });
        }

        function viewRemoteDetails(idx) {
            const s = window[`remote_record_${idx}`];
            if (!s) return;
            const pane = document.getElementById('remote-details');
            pane.style.display = 'block';
            pane.innerHTML = `
                <h4>Remote Student Details</h4>
                <div><strong>Student ID:</strong> ${sanitize(s.student_id || s.id || 'N/A')}</div>
                <div><strong>Full Name:</strong> ${sanitize(s.name || 'N/A')}</div>
                <div><strong>Program:</strong> ${sanitize(s.program || 'N/A')}</div>
                <div><strong>Year Level:</strong> ${sanitize(s.year || 'N/A')}</div>
                <div><strong>Section:</strong> ${sanitize(s.section || 'N/A')}</div>
            `;
        }

        function sanitize(str) {
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# FLASK ROUTE CONTROLLERS
# ---------------------------------------------------------

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# READ ALL
@app.route('/api/students', methods=['GET'])
def get_students():
    db = get_db()
    cursor = db.execute('SELECT * FROM students ORDER BY id DESC')
    students = [dict(row) for row in cursor.fetchall()]
    return jsonify(students), 200

# READ SINGLE BY ID
@app.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM students WHERE id = ?', (id,))
    student = cursor.fetchone()
    if student is None:
        return jsonify({"error": "Student record not found"}), 404
    return jsonify(dict(student)), 200

# CREATE
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    required_fields = ['student_id', 'name', 'program', 'year', 'section']
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO students (student_id, name, program, year, section)
           VALUES (?, ?, ?, ?, ?)""",
        (data['student_id'].strip(), data['name'].strip(), 
         data['program'].strip(), data['year'].strip(), data['section'].strip())
    )
    db.commit()
    new_id = cursor.lastrowid
    return jsonify({"message": "Student successfully created", "id": new_id}), 201

# UPDATE
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    db = get_db()
    cursor = db.execute('SELECT * FROM students WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Student record not found"}), 404

    required_fields = ['student_id', 'name', 'program', 'year', 'section']
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    db.execute(
        """UPDATE students SET student_id=?, name=?, program=?, year=?, section=?
           WHERE id=?""",
        (data['student_id'].strip(), data['name'].strip(), 
         data['program'].strip(), data['year'].strip(), data['section'].strip(), id)
    )
    db.commit()
    return jsonify({"message": "Student successfully updated"}), 200

# DELETE
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM students WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Student record not found"}), 404

    db.execute('DELETE FROM students WHERE id = ?', (id,))
    db.commit()
    return jsonify({"message": "Student successfully deleted"}), 200

# SERVER PROXY (Fallback for classmate CORS errors)
@app.route('/api/proxy/classmate', methods=['GET'])
def proxy_classmate():
    classmate_url = request.args.get('url')
    if not classmate_url:
        return jsonify({"error": "Query parameter 'url' is required"}), 400

    try:
        response = requests.get(classmate_url, timeout=7)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Proxy fetch failed: {str(e)}"}), 502

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)