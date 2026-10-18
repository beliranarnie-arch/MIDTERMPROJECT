
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DATABASE = "students.db"


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# STUDENT INFORMATION API
@app.route("/student")
def student():
    return jsonify({
        "name": "Arnie Beliran",
        "student_id": "2026-00123",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# GREETING API
@app.route("/hello")
def hello():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


# COURSE API
@app.route("/course")
def course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "program": "BSIT"
    })


# TEACHER API
@app.route("/teacher")
def teacher():
    return jsonify({
        "teacher": "Your Teacher",
        "subject": "Web Development"
    })


# SUBJECTS API
@app.route("/subjects")
def subjects():
    return jsonify({
        "subjects": [
            "Web Development",
            "Database Management",
            "Networking",
            "Programming"
        ]
    })


# SCHEDULE API
@app.route("/schedule")
def schedule():
    return jsonify({
        "schedule": "Monday to Friday",
        "time": "8:00 AM - 5:00 PM"
    })


# ABOUT API
@app.route("/about")
def about():
    return jsonify({
        "project": "MIDTERMPROJECT",
        "description": "Flask API with SQLite Database"
    })


# GENERAL API
@app.route("/api")
def api():
    return jsonify({
        "message": "Welcome to the Flask API!",
        "status": "success"
    })


# GET ALL STUDENTS
@app.route("/students")
def get_students():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# GET ONE STUDENT BY DATABASE ID
@app.route("/students/<int:id>")
def get_student(id):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "Student not found."}), 404

        return jsonify(dict(row))
    finally:
        conn.close()


# FILTER STUDENTS BY SECTION
@app.route("/students/section/<string:section>")
def get_students_by_section(section):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students WHERE UPPER(section) = ? ORDER BY id DESC",
            (section.upper(),)
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# ADD NEW STUDENT
@app.route("/students/add", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).strip().upper()
    section = str(data.get("section", "")).strip().upper()

    try:
        year = int(data.get("year", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number."}), 400

    if not all([student_id, name, program, section]):
        return jsonify({"error": "Please fill in all fields."}), 400

    if year not in [1, 2, 3, 4]:
        return jsonify({"error": "Year must be between 1 and 4."}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO students
                (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, name, program, year, section)
        )
        conn.commit()

        return jsonify({
            "message": "Student added successfully!",
            "student_id": student_id,
            "name": name
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists."}), 409
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
