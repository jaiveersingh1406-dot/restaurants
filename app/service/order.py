from datetime import date

from app.db.db import get_connection
from fastapi import HTTPException


def _serialize(row):
    data = dict(row)
    data.pop("items", None)
    return data


def get_order(order_id: int):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return _serialize(result) if result else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_orders(status=None, payment_status=None):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM orders"
        clauses = []
        params = []

        if status:
            clauses.append("status = %s")
            params.append(status)

        if payment_status:
            clauses.append("payment_status = %s")
            params.append(payment_status)

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return [_serialize(row) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_order(order_data):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO orders
               (customer_name, phone, email, table_no, total, status,
                payment_id, razorpay_order_id, razorpay_signature,
                payment_method, payment_status, amount_paid)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                order_data.customer_name,
                order_data.phone,
                getattr(order_data, "email", None),
                order_data.table_no,
                order_data.total,
                order_data.status,
                getattr(order_data, "payment_id", None),
                getattr(order_data, "razorpay_order_id", None),
                getattr(order_data, "razorpay_signature", None),
                getattr(order_data, "payment_method", None),
                getattr(order_data, "payment_status", None),
                getattr(order_data, "amount_paid", None),
            )
        )

        connection.commit()
        order_id = cursor.lastrowid

        if order_data.table_no:
            cursor.execute(
                """INSERT INTO reservations
                   (customer_name, phone, guests, reservation_date,
                    time_slot, table_no, special_request, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 'Confirmed')""",
                (
                    order_data.customer_name,
                    order_data.phone,
                    1,
                    str(date.today()),
                    "Dine-in Order",
                    order_data.table_no,
                    f"Auto-booked from order #{order_id}",
                ),
            )
            connection.commit()

        cursor.close()
        connection.close()

        return get_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_order_status(order_id: int, status: str):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Order not found")

        cursor.close()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (status, order_id),
        )
        connection.commit()

        cursor.close()
        connection.close()

        return get_order(order_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_order(order_id: int):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            connection.close()
            return None

        cursor.close()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return _serialize(existing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
