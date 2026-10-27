
import os
import sqlite3
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "students.db")

# Set this environment variable to your classmate's public API URL.
CLASSMATE_API_URL = os.environ.get("CLASSMATE_API_URL", "").strip()

FIELDS = ("student_id", "name", "program", "year", "section")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def student_from_request():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, "Please send student data as JSON."

    student = {
        field: str(data.get(field, "")).strip()
        for field in FIELDS
    }

    if any(not value for value in student.values()):
        return None, "All five student fields are required."

    return student, None


@app.route("/")
def index():
    return render_template("index.html")


# READ: Retrieve all records from your own SQLite database.
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# CREATE: Add a student.
@app.route("/api/students", methods=["POST"])
def add_student():
    student, error = student_from_request()

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, tuple(student[field] for field in FIELDS))

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully.",
            "id": new_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "That Student ID already exists."
        }), 409

    finally:
        conn.close()


# READ: Retrieve one student by database ID.
@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found."}), 404

    return jsonify(dict(student))


# UPDATE: Edit a student in your own database.
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    student, error = student_from_request()

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE students
            SET student_id = ?, name = ?, program = ?,
                year = ?, section = ?
            WHERE id = ?
        """, tuple(student[field] for field in FIELDS) + (id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        return jsonify({"message": "Student updated successfully."})

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "That Student ID already belongs to another record."
        }), 409

    finally:
        conn.close()


# DELETE: Delete a student from your own database.
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student deleted successfully."})


# READ-ONLY PROXY: Retrieve your classmate's records.
# The remote URL is configured on the server, not supplied by the browser.
@app.route("/api/classmate", methods=["GET"])
def get_classmate_records():
    if not CLASSMATE_API_URL:
        return jsonify({
            "error": "Classmate API is not configured yet."
        }), 400

    parsed_url = urlparse(CLASSMATE_API_URL)

    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname is None
        or not parsed_url.hostname.endswith(".onrender.com")
        or parsed_url.username
        or parsed_url.password
    ):
        return jsonify({
            "error": "Configure a valid HTTPS Render API URL."
        }), 400

    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=15,
            allow_redirects=False
        )
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "The classmate API did not return a list."
            }), 502

        # Only accept a list of student record objects.
        if not all(isinstance(record, dict) for record in records):
            return jsonify({
                "error": "The classmate API returned an invalid format."
            }), 502

        return jsonify(records)

    except (requests.RequestException, ValueError):
        return jsonify({
            "error": "Could not retrieve the classmate's API records."
        }), 502


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
