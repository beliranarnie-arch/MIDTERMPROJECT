
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import requests

app = Flask(__name__)

DATABASE = os.path.join(app.root_path, "students.db")
PARTNER_API_URL =export PARTNER_API_URL="https://YOUR-CLASSMATE-APP.onrender.com/api/students"
python app.py


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INITIALIZE DATABASE ----------------

def initialize_database():
    conn = get_db_connection()

    try:
        conn.execute("""
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

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        }

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
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
    finally:
        conn.close()


# ---------------- VALIDATE STUDENT DATA ----------------

def validate_student(data):
    if not isinstance(data, dict):
        return None, "Valid JSON is required."

    fields = ["student_id", "name", "program", "year", "section"]

    for field in fields:
        value = data.get(field)

        if value is None or str(value).strip() == "":
            return None, "All student fields are required."

    try:
        year = int(data["year"])
        if not 1 <= year <= 6:
            return None, "Year must be between 1 and 6."
    except (ValueError, TypeError, OverflowError):
        return None, "Year must be between 1 and 6."

    return {
        "student_id": str(data["student_id"]).strip(),
        "name": str(data["name"]).strip(),
        "program": str(data["program"]).strip(),
        "year": year,
        "section": str(data["section"]).strip().upper()
    }, None


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- API DOCUMENTATION ----------------

@app.route("/api", methods=["GET"])
def api_documentation():
    return jsonify({
        "application": "Student Information API",
        "developer": "Arnie Beliran",
        "database": "SQLite",
        "endpoints": {
            "read_all": "GET /api/students",
            "create": "POST /api/students",
            "read_one": "GET /api/students/<id>",
            "update": "PUT /api/students/<id>",
            "delete": "DELETE /api/students/<id>",
            "classmate_records": "GET /partner-records"
        }
    }), 200


# ---------------- READ ALL STUDENTS ----------------

@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    finally:
        conn.close()


# ---------------- CREATE STUDENT ----------------

@app.route("/api/students", methods=["POST"])
def create_student():
    student, error = validate_student(
        request.get_json(silent=True)
    )

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, 'Local')
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


# ---------------- READ ONE STUDENT ----------------

@app.route("/api/students/<int:id>", methods=["GET"])
def get_student(id):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "Student not found."}), 404

        return jsonify(dict(row)), 200
    finally:
        conn.close()


# ---------------- UPDATE STUDENT ----------------

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    student, error = validate_student(
        request.get_json(silent=True)
    )

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            UPDATE students
            SET student_id = ?, name = ?, program = ?,
                year = ?, section = ?
            WHERE id = ?
        """, (
            student["student_id"],
            student["name"],
            student["program"],
            student["year"],
            student["section"],
            id
        ))

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        conn.commit()
        return jsonify({
            "message": "Student updated successfully."
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409
    finally:
        conn.close()


# ---------------- DELETE STUDENT ----------------

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        conn.commit()
        return jsonify({
            "message": "Student deleted successfully."
        }), 200
    finally:
        conn.close()


# ---------------- RETRIEVE CLASSMATE RECORDS ----------------
# Read-only: this endpoint does not change the classmate's database.

@app.route("/partner-records", methods=["GET"])
def partner_records():
    if not PARTNER_API_URL:
        return jsonify({
            "error": "Classmate API URL is not configured. "
                     "Set PARTNER_API_URL in your environment."
        }), 503

    try:
        response = requests.get(PARTNER_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Classmate API must return a JSON list."
            }), 502

        return jsonify(data), 200

    except requests.RequestException:
        app.logger.exception("Classmate API request failed.")
        return jsonify({
            "error": "Could not retrieve classmate records. "
                     "Check the API URL and availability."
        }), 502

    except ValueError:
        return jsonify({
            "error": "Classmate API did not return valid JSON."
        }), 502


# ---------------- START APPLICATION ----------------

initialize_database()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
