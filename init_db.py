import sqlite3

def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Drop existing table to ensure a clean schema reset
    cursor.execute('DROP TABLE IF EXISTS students')

    # Create students table
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL
        )
    ''')

    # Insert initial practice records
    sample_students = [
        ('2026-0001', 'Juan Dela Cruz', 'BSIT', '3rd Year', '3A'),
        ('2026-0002', 'Maria Santos', 'BSCS', '2nd Year', '2B')
    ]

    cursor.executemany('''
        INSERT INTO students (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_students)

    conn.commit()
    conn.close()
    print("Success: 'students.db' initialized with sample data.")

if __name__ == '__main__':
    init_db()