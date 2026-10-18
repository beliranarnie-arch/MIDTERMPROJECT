

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Arnie's Flask API!"
    })


@app.route("/student", methods=["GET"])
def student():
    return jsonify({
        "student_id": "2026-001",
        "name": "Arnie Beliran",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


@app.route("/hello", methods=["GET"])
def hello():
    name = request.args.get("name", "Student")
    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route("/about", methods=["GET"])
def about():
    return jsonify({
        "api_name": "Arnie's Student API",
        "developer": "Arnie Beliran",
        "purpose": "Student information management",
        "version": "1.0"
    })


@app.route("/course", methods=["GET"])
def course():
    return jsonify({
        "course_code": "IT101",
        "course_name": "Introduction to Programming",
        "program": "BSIT",
        "units": 3
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
