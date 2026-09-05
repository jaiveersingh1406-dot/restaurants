from app.db.db import get_connection
from fastapi import HTTPException


def get_reservation(reservation_id: int):
    """Fetch a single reservation by ID"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM reservations WHERE id = %s",
            (reservation_id,)
        )

        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_reservations(status=None):
    """Fetch all reservations"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM reservations"
        if status:
            query += " WHERE status = %s"

        query += " ORDER BY id DESC"
        cursor.execute(query, (status,) if status else ())
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_reservation(reservation_data):
    """Create a new reservation"""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO reservations
               (customer_name, guests, reservation_date, time_slot, phone, table_no, special_request, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                reservation_data.customer_name,
                reservation_data.guests,
                reservation_data.reservation_date or None,
                reservation_data.time_slot,
                reservation_data.phone or None,
                reservation_data.table_no,
                reservation_data.special_request or None,
                reservation_data.status
            )
        )

        connection.commit()
        reservation_id = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return get_reservation(reservation_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_reservation(reservation_id: int, reservation_data):
    """Update an existing reservation"""
    try:
        existing = get_reservation(reservation_id)

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Reservation not found"
            )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE reservations
            SET
                customer_name = %s,
                guests = %s,
                reservation_date = %s,
                time_slot = %s,
                phone = %s,
                table_no = %s,
                special_request = %s,
                status = %s
            WHERE id = %s
            """,
            (
                reservation_data.customer_name,
                reservation_data.guests,
                reservation_data.reservation_date or None,
                reservation_data.time_slot,
                reservation_data.phone or None,
                reservation_data.table_no,
                reservation_data.special_request or None,
                reservation_data.status,
                reservation_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return get_reservation(reservation_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def update_reservation_status(reservation_id: int, status: str):
    """Update only the status of a reservation"""
    try:
        existing = get_reservation(reservation_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Reservation not found")

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE reservations SET status = %s WHERE id = %s",
            (status, reservation_id),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return get_reservation(reservation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_reservation(reservation_id: int):
    try:
        existing = get_reservation(reservation_id)
        if not existing:
            return None
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return existing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
