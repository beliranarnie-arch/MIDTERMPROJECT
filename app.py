
import sqlite3
import requests
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={
    r"/api/students*": {"origins": "*"}
})

DATABASE = 'students.db'
CLASSMATE_HOST = 'jasminerose-2.onrender.com'


# =========================================================
# DATABASE CONNECTION
# =========================================================

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


# =========================================================
# HOME PAGE
# =========================================================

@app.route('/')
def index():
    return render_template('index.html')


# =========================================================
# STUDENT INFORMATION API
# GET: /student
# =========================================================

@app.route('/student', methods=['GET'])
def student_information():
    return jsonify({
        "student_id": "2026-00123",
        "name": "Arnie Beliran",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    }), 200


# =========================================================
# GREETING API
# GET: /hello?name=Arnie
# =========================================================

@app.route('/hello', methods=['GET'])
def hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({
        "message": f"Hello, {name}! Welcome to Student Information System."
    }), 200


# =========================================================
# COURSE API
# GET: /course
# =========================================================

@app.route('/course', methods=['GET'])
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    }), 200


# =========================================================
# TEACHER API
# GET: /teacher
# =========================================================

@app.route('/teacher', methods=['GET'])
def get_teacher():
    return jsonify({
        "teacher_id": "T001",
        "name": "Juan Dela Cruz",
        "department": "IT",
        "subject": "Web Development"
    }), 200


# =========================================================
# SUBJECTS API
# GET: /subjects
# =========================================================

@app.route('/subjects', methods=['GET'])
def get_subjects():
    return jsonify({
        "subjects": [
            "Web Development",
            "Database Management",
            "Networking",
            "Programming"
        ]
    }), 200


# =========================================================
# SCHEDULE API
# GET: /schedule
# =========================================================

@app.route('/schedule', methods=['GET'])
def get_schedule():
    return jsonify({
        "day": "Monday",
        "time": "8:00 AM - 10:00 AM",
        "subject": "Web Development",
        "room": "Computer Laboratory 1"
    }), 200


# =========================================================
# ABOUT API
# GET: /about
# =========================================================

@app.route('/about', methods=['GET'])
def get_about():
    return jsonify({
        "application": "Student Information System",
        "developer": "Arnie Beliran",
        "framework": "Python Flask"
    }), 200


# =========================================================
# GENERAL API
# GET: /api
# =========================================================

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        "message": "Welcome to Student Information API",
        "available_endpoints": [
            "/student",
            "/hello",
            "/course",
            "/teacher",
            "/subjects",
            "/schedule",
            "/about",
            "/api/students"
        ]
    }), 200


# =========================================================
# READ ALL STUDENTS
# GET: /api/students
# =========================================================

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        db = get_db()

        cursor = db.execute(
            'SELECT * FROM students ORDER BY id DESC'
        )

        students = [dict(row) for row in cursor.fetchall()]

        return jsonify(students), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# READ ONE STUDENT
# GET: /api/students/1
# =========================================================

@app.route('/api/students/<int:id>', methods=['GET'])
def get_one_student(id):
    try:
        db = get_db()

        student = db.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student record not found"
            }), 404

        return jsonify(dict(student)), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# CREATE STUDENT
# POST: /api/students
# =========================================================

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid or missing JSON data"
        }), 400

    fields = ['student_id', 'name', 'program', 'year', 'section']

    for field in fields:
        if data.get(field) is None or not str(data[field]).strip():
            return jsonify({
                "error": f"{field} is required"
            }), 400

    try:
        db = get_db()

        cursor = db.execute("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(data['student_id']).strip(),
            str(data['name']).strip(),
            str(data['program']).strip(),
            str(data['year']).strip(),
            str(data['section']).strip()
        ))

        db.commit()

        return jsonify({
            "message": "Student successfully added",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# UPDATE STUDENT
# PUT: /api/students/1
# =========================================================

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid or missing JSON data"
        }), 400

    fields = ['student_id', 'name', 'program', 'year', 'section']

    for field in fields:
        if data.get(field) is None or not str(data[field]).strip():
            return jsonify({
                "error": f"{field} is required"
            }), 400

    try:
        db = get_db()

        student = db.execute(
            'SELECT id FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student record not found"
            }), 404

        db.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
        """, (
            str(data['student_id']).strip(),
            str(data['name']).strip(),
            str(data['program']).strip(),
            str(data['year']).strip(),
            str(data['section']).strip(),
            id
        ))

        db.commit()

        return jsonify({
            "message": "Student successfully updated",
            "id": id
        }), 200

    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# DELETE STUDENT
# DELETE: /api/students/1
# =========================================================

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        db = get_db()

        student = db.execute(
            'SELECT id FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student record not found"
            }), 404

        db.execute(
            'DELETE FROM students WHERE id = ?',
            (id,)
        )

        db.commit()

        return jsonify({
            "message": "Student successfully deleted",
            "id": id
        }), 200

    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# CLASSMATE REMOTE API
# GET: /api/proxy/classmate?url=...
# READ ONLY
# =========================================================

@app.route('/api/proxy/classmate', methods=['GET'])
def proxy_classmate():
    classmate_url = request.args.get('url', '').strip()

    if not classmate_url:
        classmate_url = (
            'https://jasminerose-2.onrender.com/api/students'
        )

    parsed_url = urlparse(classmate_url)

    if (
        parsed_url.scheme != 'https'
        or parsed_url.hostname != CLASSMATE_HOST
        or parsed_url.username
        or parsed_url.password
        or parsed_url.path != '/api/students'
    ):
        return jsonify({
            "error": "Invalid classmate API URL. Use the approved HTTPS student API URL."
        }), 400

    try:
        response = requests.get(
            classmate_url,
            timeout=60,
            allow_redirects=False,
            headers={"Accept": "application/json"}
        )

        response.raise_for_status()

        remote_data = response.json()

        if not isinstance(remote_data, (list, dict)):
            return jsonify({
                "error": "Invalid data returned by classmate API"
            }), 502

        return jsonify(remote_data), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Classmate API connection timed out"
        }), 504

    except requests.exceptions.HTTPError as e:
        return jsonify({
            "error": f"Classmate API HTTP error: {str(e)}"
        }), 502

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Unable to connect to classmate API: {str(e)}"
        }), 502

    except ValueError:
        return jsonify({
            "error": "Classmate API did not return valid JSON"
        }), 502


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
