from app.db.db import get_connection
from fastapi import HTTPException

TABLES = ["T-01", "T-02", "T-04", "T-05", "T-10"]


def get_availability(date: str, time_slot: str):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """SELECT table_no, status FROM reservations
               WHERE reservation_date = %s
                 AND time_slot = %s
                 AND status != 'Cancelled'""",
            (date, time_slot),
        )
        booked_rows = cursor.fetchall()

        cursor.close()
        connection.close()

        booked_tables = {
            row["table_no"]: row["status"] for row in booked_rows
        }

        tables = [
            {
                "table_no": table_no,
                "status": "Booked" if table_no in booked_tables else "Free",
            }
            for table_no in TABLES
        ]

        free_count = sum(1 for table in tables if table["status"] == "Free")

        return {
            "date": date,
            "time_slot": time_slot,
            "free_count": free_count,
            "tables": tables,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
