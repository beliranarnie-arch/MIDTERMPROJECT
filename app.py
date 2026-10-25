
from flask import Flask, jsonify, request, render_template
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "student-information-secret-key"

DATABASE = "students.db"
CLASSMATE_API_URL = "https://jasminerose-2.onrender.com/api/students"


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# VALIDATE STUDENT DATA
def valid_student_data(data):
    required = ["student_id", "name", "program", "year", "section"]

    if not isinstance(data, dict):
        return None, "Request must contain a JSON object."

    for field in required:
        if field not in data or str(data[field]).strip() == "":
            return None, f"Missing required field: {field}"

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return None, "Year must be a number from 1 to 6."

    if not 1 <= year <= 6:
        return None, "Year must be a number from 1 to 6."

    student = {
        "student_id": str(data["student_id"]).strip(),
        "name": str(data["name"]).strip(),
        "program": str(data["program"]).strip().upper(),
        "year": year,
        "section": str(data["section"]).strip().upper()
    }

    return student, None


# HOME PAGE
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# CRUD: READ ALL STUDENTS
# GET /api/students
# ==========================================
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# ==========================================
# CRUD: CREATE STUDENT
# POST /api/students
# ==========================================
@app.route("/api/students", methods=["POST"])
def api_add_student():
    data = request.get_json(silent=True)
    student, error = valid_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student["student_id"],
            student["name"],
            student["program"],
            student["year"],
            student["section"]
        ))

        conn.commit()

        return jsonify({
            "message": "Student added successfully.",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    finally:
        conn.close()


# ==========================================
# CRUD: READ ONE STUDENT
# GET /api/students/1
# ==========================================
@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found."}), 404

        return jsonify(dict(student))
    finally:
        conn.close()


# ==========================================
# CRUD: UPDATE STUDENT
# PUT /api/students/1
# ==========================================
@app.route("/api/students/<int:id>", methods=["PUT"])
def api_update_student(id):
    data = request.get_json(silent=True)
    student, error = valid_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (id,)
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
            student["student_id"],
            student["name"],
            student["program"],
            student["year"],
            student["section"],
            id
        ))

        conn.commit()

        return jsonify({
            "message": "Student updated successfully."
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    finally:
        conn.close()


# ==========================================
# CRUD: DELETE STUDENT
# DELETE /api/students/1
# ==========================================
@app.route("/api/students/<int:id>", methods=["DELETE"])
def api_delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        return jsonify({
            "message": "Student deleted successfully."
        })

    finally:
        conn.close()


# ==========================================
# CLASSMATE API: READ-ONLY
# ==========================================
@app.route("/api/classmate/students", methods=["GET"])
def api_classmate_students():
    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=45
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Classmate API did not return a list of records."
            }), 502

        return jsonify(data)

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to retrieve classmate records.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "Classmate API did not return valid JSON."
        }), 502


# ==========================================
# ORIGINAL STUDENT API
# ==========================================
@app.route("/student", methods=["GET"])
def student():
    return jsonify({
        "student_id": "2026-00123",
        "name": "Arnie Beliran",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# ==========================================
# GREETING API
# ==========================================
@app.route("/hello", methods=["GET"])
def hello():
    name = request.args.get("name", "Student").strip()

    if not name:
        name = "Student"

    return jsonify({"message": f"Hello, {name}!"})


# ==========================================
# COURSE API
# ==========================================
@app.route("/course", methods=["GET"])
def course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# ==========================================
# API ENDPOINT LIST
# ==========================================
@app.route("/api", methods=["GET"])
def api():
    return jsonify({
        "message": "Student Information API",
        "endpoints": {
            "home": "GET /",
            "read_all": "GET /api/students",
            "create": "POST /api/students",
            "read_one": "GET /api/students/<id>",
            "update": "PUT /api/students/<id>",
            "delete": "DELETE /api/students/<id>",
            "classmate_records": "GET /api/classmate/students",
            "student": "GET /student",
            "hello": "GET /hello?name=Arnie",
            "course": "GET /course"
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
