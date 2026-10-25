
import os
import sqlite3

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")


def initialize_database():
    conn = sqlite3.connect(DATABASE)

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
            row[1]
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
        print("Database initialized successfully.")

    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
