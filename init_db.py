
import sqlite3

DATABASE = "students.db"


def initialize_database():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    # Add the source column if the table is from an older activity.
    columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    ]

    if "source" not in columns:
        conn.execute("""
            ALTER TABLE students
            ADD COLUMN source TEXT DEFAULT 'Local'
        """)

    # Label existing records without a source as Local.
    conn.execute("""
        UPDATE students
        SET source = 'Local'
        WHERE source IS NULL OR source = ''
    """)

    # Add Arnie's record only if the student ID is not already present.
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
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
