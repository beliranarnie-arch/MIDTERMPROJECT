import sqlite3

def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Create table only if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL
        )
    ''')

    # Seed initial data only if table is currently empty
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('2026-0001', 'Juan Dela Cruz', 'BSIT', '3rd Year', '3A'),
            ('2026-0002', 'Maria Santos', 'BSCS', '2nd Year', '2B')
        ]
        cursor.executemany('''
            INSERT INTO students (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_students)
        print("Sample data inserted.")

    conn.commit()
    conn.close()
    print("Success: Database initialized.")

if __name__ == '__main__':
    init_db()