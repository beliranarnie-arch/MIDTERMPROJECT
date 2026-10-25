
import sqlite3

DATABASE = "students.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE - Add a new student
def create_student():
    print("\n=== CREATE STUDENT ===")

    student_id = input("Student ID: ").strip()
    name = input("Full Name: ").strip()
    program = input("Program: ").strip().upper()
    year = input("Year Level: ").strip()
    section = input("Section: ").strip().upper()

    if not all([student_id, name, program, year, section]):
        print("Error: All fields are required.")
        return

    try:
        year = int(year)

        with get_connection() as conn:
            conn.execute("""
                INSERT INTO students
                (student_id, name, program, year, section)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, name, program, year, section))

        print("Student created successfully!")

    except ValueError:
        print("Error: Year level must be a number.")
    except sqlite3.IntegrityError:
        print("Error: Student ID already exists.")


# READ - Display all students
def read_students():
    print("\n=== STUDENT RECORDS ===")

    with get_connection() as conn:
        students = conn.execute("""
            SELECT * FROM students ORDER BY id
        """).fetchall()

    if not students:
        print("No student records found.")
        return

    print("-" * 85)
    print(f"{'ID':<5} {'Student ID':<15} {'Name':<22} "
          f"{'Program':<10} {'Year':<6} {'Section':<8}")
    print("-" * 85)

    for student in students:
        print(
            f"{student['id']:<5} "
            f"{student['student_id']:<15} "
            f"{student['name']:<22} "
            f"{student['program']:<10} "
            f"{student['year']:<6} "
            f"{student['section']:<8}"
        )

    print("-" * 85)


# UPDATE - Modify an existing student
def update_student():
    print("\n=== UPDATE STUDENT ===")

    try:
        record_id = int(input("Enter database ID to update: "))

        with get_connection() as conn:
            student = conn.execute("""
                SELECT * FROM students WHERE id = ?
            """, (record_id,)).fetchone()

            if student is None:
                print("Student record not found.")
                return

            print("Press Enter to keep the current value.")

            student_id = input(
                f"Student ID [{student['student_id']}]: "
            ).strip() or student["student_id"]

            name = input(
                f"Name [{student['name']}]: "
            ).strip() or student["name"]

            program = input(
                f"Program [{student['program']}]: "
            ).strip().upper() or student["program"]

            year_input = input(
                f"Year [{student['year']}]: "
            ).strip()

            section = input(
                f"Section [{student['section']}]: "
            ).strip().upper() or student["section"]

            year = int(year_input) if year_input else student["year"]

            conn.execute("""
                UPDATE students
                SET student_id = ?,
                    name = ?,
                    program = ?,
                    year = ?,
                    section = ?
                WHERE id = ?
            """, (
                student_id, name, program, year, section, record_id
            ))

        print("Student updated successfully!")

    except ValueError:
        print("Error: Database ID and year must be numbers.")
    except sqlite3.IntegrityError:
        print("Error: Student ID already exists.")


# DELETE - Remove a student
def delete_student():
    print("\n=== DELETE STUDENT ===")

    try:
        record_id = int(input("Enter database ID to delete: "))

        with get_connection() as conn:
            student = conn.execute("""
                SELECT * FROM students WHERE id = ?
            """, (record_id,)).fetchone()

            if student is None:
                print("Student record not found.")
                return

            print(f"Student: {student['name']}")
            confirm = input("Are you sure you want to delete? (yes/no): ")

            if confirm.strip().lower() != "yes":
                print("Delete cancelled.")
                return

            conn.execute("""
                DELETE FROM students WHERE id = ?
            """, (record_id,))

        print("Student deleted successfully!")

    except ValueError:
        print("Error: Please enter a valid database ID.")


# MAIN MENU
def main():
    while True:
        print("\n================================")
        print(" STUDENT CRUD MANAGEMENT SYSTEM")
        print("================================")
        print("1. Create Student")
        print("2. Read All Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")
        print("================================")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            create_student()
        elif choice == "2":
            read_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Thank you for using the CRUD system!")
            break
        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()
