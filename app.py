import os
import csv
import io
from datetime import date, datetime
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, Response
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_

app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "change-this-secret-key"
)

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Render PostgreSQL connection compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///laboratory.db"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


# DATABASE MODEL
class LabData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_name = db.Column(db.String(150), nullable=False)
    result = db.Column(db.Text, nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# HOME / DASHBOARD
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    query = LabData.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                LabData.sample_name.ilike(pattern),
                LabData.result.ilike(pattern),
                LabData.notes.ilike(pattern)
            )
        )

    records = query.order_by(LabData.id.desc()).all()
    total_records = LabData.query.count()

    return render_template(
        "index.html",
        records=records,
        total_records=total_records,
        search=search,
        today=date.today().isoformat()
    )


# SAVE DATA
@app.route("/save", methods=["POST"])
def save_data():
    sample_name = request.form.get("sample_name", "").strip()
    result = request.form.get("result", "").strip()
    test_date = request.form.get("test_date", "").strip()
    notes = request.form.get("notes", "").strip()

    if not sample_name or not result or not test_date:
        flash("Please complete all required fields.", "danger")
        return redirect(url_for("index"))

    try:
        parsed_date = date.fromisoformat(test_date)
    except ValueError:
        flash("Invalid test date.", "danger")
        return redirect(url_for("index"))

    record = LabData(
        sample_name=sample_name,
        result=result,
        test_date=parsed_date,
        notes=notes
    )

    db.session.add(record)
    db.session.commit()

    flash("Laboratory data saved successfully!", "success")
    return redirect(url_for("index"))


# RETRIEVE / VIEW RECORD
@app.route("/record/<int:record_id>")
def retrieve_data(record_id):
    record = db.get_or_404(LabData, record_id)
    return {
        "id": record.id,
        "sample_name": record.sample_name,
        "result": record.result,
        "test_date": record.test_date.isoformat(),
        "notes": record.notes,
        "created_at": record.created_at.isoformat()
    }


# DELETE DATA
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_data(record_id):
    record = db.get_or_404(LabData, record_id)

    db.session.delete(record)
    db.session.commit()

    flash("Laboratory record deleted successfully!", "success")
    return redirect(url_for("index"))


# SEND / EXPORT DATA TO CSV
@app.route("/export")
def export_data():
    records = LabData.query.order_by(LabData.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Sample Name",
        "Laboratory Result",
        "Test Date",
        "Notes",
        "Date Created"
    ])

    for record in records:
        values = [
            record.id,
            record.sample_name,
            record.result,
            record.test_date.isoformat(),
            record.notes or "",
            record.created_at.isoformat()
        ]

        # Reduce spreadsheet formula-injection risk
        safe_values = [
            "'" + value if isinstance(value, str)
            and value.startswith(("=", "+", "-", "@"))
            else value
            for value in values
        ]

        writer.writerow(safe_values)

    response = Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=laboratory_data.csv"
    )

    return response


# CREATE DATABASE TABLES
with app.app_context():
    db.create_all()


# RUN APPLICATION
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
