
import sqlite3

DATABASE = "students.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create the students table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # Insert initial practice records only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:

        sample_students = [
            ('2026-0001', 'Juan Dela Cruz', 'BSIT', 3, 'A'),
            ('2026-0002', 'Maria Santos', 'BSCS', 2, 'B')
        ]

        cursor.executemany("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, sample_students)

        print("Initial practice records inserted.")

    else:
        print("Existing student records preserved.")

    conn.commit()
    conn.close()

    print("Success: students.db is ready!")


if __name__ == "__main__":
    init_db()
