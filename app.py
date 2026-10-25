
from flask import Flask, jsonify, request
import sqlite3
import requests

app = Flask(__name__)
DATABASE = "students.db"

CLASSMATE_API_URL = "https://jasminerose-2.onrender.com"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def student_to_dict(student):
    return dict(student)


@app.route("/")
def home():
    return """
    <h1>Student Information System</h1>
    <p>Flask API with SQLite Database</p>
    <h3>Available Endpoints</h3>
    <ul>
        <li><a href="/api/students">View All Students</a></li>
        <li><a href="/api">View API Information</a></li>
        <li><a href="/api/classmate/students">View Classmate API</a></li>
    </ul>
    <p>Use a REST client or the terminal CRUD program
    to create, update, and delete records.</p>
    """


@app.route("/api")
def api_info():
    return jsonify({
        "message": "Student Information API",
        "endpoints": {
            "all_students": "GET /api/students",
            "create_student": "POST /api/students",
            "single_student": "GET /api/students/<id>",
            "update_student": "PUT /api/students/<id>",
            "delete_student": "DELETE /api/students/<id>",
            "classmate_students": "GET /api/classmate/students"
        }
    })


@app.route("/api/students", methods=["GET", "POST"])
def students():
    if request.method == "GET":
        with get_db_connection() as conn:
            records = conn.execute(
                "SELECT * FROM students ORDER BY id"
            ).fetchall()

        return jsonify([student_to_dict(row) for row in records])

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Provide a JSON object."}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if any(
        key not in data or str(data[key]).strip() == ""
        for key in required
    ):
        return jsonify({"error": "All student fields are required."}), 400

    try:
        year = int(data["year"])
        if year < 1 or year > 6:
            return jsonify({"error": "Year must be from 1 to 6."}), 400

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


@app.route("/api/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def student_detail(student_id):
    if request.method == "GET":
        with get_db_connection() as conn:
            student = conn.execute(
                "SELECT * FROM students WHERE id = ?",
                (student_id,)
            ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found."}), 404

        return jsonify(student_to_dict(student))

    if request.method == "PUT":
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Provide a JSON object."}), 400

        required = ["student_id", "name", "program", "year", "section"]

        if any(
            key not in data or str(data[key]).strip() == ""
            for key in required
        ):
            return jsonify({"error": "All student fields are required."}), 400

        try:
            year = int(data["year"])
            if year < 1 or year > 6:
                return jsonify({"error": "Year must be from 1 to 6."}), 400

            with get_db_connection() as conn:
                existing = conn.execute(
                    "SELECT id FROM students WHERE id = ?",
                    (student_id,)
                ).fetchone()

                if existing is None:
                    return jsonify({"error": "Student not found."}), 404

                conn.execute("""
                    UPDATE students
                    SET student_id = ?, name = ?, program = ?,
                        year = ?, section = ?
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

    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student deleted successfully."})


@app.route("/api/classmate/students", methods=["GET"])
def classmate_students():
    try:
        response = requests.get(
            f"{CLASSMATE_API_URL}/api/students",
            timeout=45
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to retrieve classmate API data.",
            "details": str(error)
        }), 502


if __name__ == "__main__":
    app.run(debug=True)
