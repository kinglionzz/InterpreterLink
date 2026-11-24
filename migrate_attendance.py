
from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.begin() as connection:

        # Check existing columns
        columns = [
            row[1]
            for row in connection.execute(
                text("PRAGMA table_info(assignments)")
            ).fetchall()
        ]

        # Add missing attendance columns
        if 'attendance_status' not in columns:
            connection.execute(text("""
                ALTER TABLE assignments
                ADD COLUMN attendance_status VARCHAR(30)
                DEFAULT 'Not Yet Confirmed'
            """))

            # Preserve existing attendance records
            connection.execute(text("""
                UPDATE assignments
                SET attendance_status = status
                WHERE status IN ('Present', 'Absent')
            """))

        if 'marked_by_student' not in columns:
            connection.execute(text("""
                ALTER TABLE assignments
                ADD COLUMN marked_by_student VARCHAR(20)
            """))

        if 'marked_by_interpreter' not in columns:
            connection.execute(text("""
                ALTER TABLE assignments
                ADD COLUMN marked_by_interpreter VARCHAR(20)
            """))

        if 'marked_at' not in columns:
            connection.execute(text("""
                ALTER TABLE assignments
                ADD COLUMN marked_at DATETIME
            """))

    print("Attendance database migration completed successfully!")
