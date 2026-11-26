
from app import app, db
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)

    columns = [
        column['name']
        for column in inspector.get_columns('timetables')
    ]

    with db.engine.begin() as connection:

        if 'approval_status' not in columns:
            connection.execute(text("""
                ALTER TABLE timetables
                ADD COLUMN approval_status VARCHAR(20)
                NOT NULL DEFAULT 'Approved'
            """))

        if 'approved_by' not in columns:
            connection.execute(text("""
                ALTER TABLE timetables
                ADD COLUMN approved_by INTEGER
            """))

        if 'approved_at' not in columns:
            connection.execute(text("""
                ALTER TABLE timetables
                ADD COLUMN approved_at DATETIME
            """))

        if 'rejection_reason' not in columns:
            connection.execute(text("""
                ALTER TABLE timetables
                ADD COLUMN rejection_reason TEXT
            """))

    print("Timetable approval migration completed successfully!")
