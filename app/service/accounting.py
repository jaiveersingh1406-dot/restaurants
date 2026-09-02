from app.db.db import get_connection
from fastapi import HTTPException


def get_accounting(accounting_id: int):
    """Fetch a single accounting entry by ID"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM accounting WHERE id = %s",
            (accounting_id,)
        )

        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_accountings():
    """Fetch all accounting entries"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM accounting ORDER BY id DESC")
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_sales_summary(period="all"):
    """Aggregate sales data (revenue/expenses/profit/orders) from real DB rows.

    period filter applies on the accounting table; 'day'/'week'/'month' limit
    to the latest rows based on their creation order.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        base_query = "SELECT * FROM accounting"

        if period in ("day", "week", "month"):
            limit = {"day": 1, "week": 7, "month": 30}[period]
            base_query += " ORDER BY id DESC LIMIT %s"
            rows = _fetch_all(cursor, base_query, (limit,))
        else:
            base_query += " ORDER BY id ASC"
            rows = _fetch_all(cursor, base_query)

        total_revenue = sum(float(r["revenue"] or 0) for r in rows)
        total_expenses = sum(float(r["expenses"] or 0) for r in rows)
        total_orders = sum(int(r["orders"] or 0) for r in rows)

        cursor.close()
        connection.close()

        return {
            "period": period,
            "entries_count": len(rows),
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": total_revenue - total_expenses,
            "total_orders": total_orders,
            "entries": rows,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _fetch_all(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchall()


def create_accounting(accounting_data):
    """Create a new accounting entry"""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO accounting
               (day, revenue, expenses, orders)
               VALUES (%s, %s, %s, %s)""",
            (
                accounting_data.day,
                accounting_data.revenue,
                accounting_data.expenses,
                accounting_data.orders
            )
        )

        connection.commit()
        accounting_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return get_accounting(accounting_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_accounting(accounting_id: int, accounting_data):
    """Update an existing accounting entry"""
    try:
        existing = get_accounting(accounting_id)

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Accounting entry not found"
            )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE accounting
            SET
                day = %s,
                revenue = %s,
                expenses = %s,
                orders = %s
            WHERE id = %s
            """,
            (
                accounting_data.day,
                accounting_data.revenue,
                accounting_data.expenses,
                accounting_data.orders,
                accounting_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return get_accounting(accounting_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def delete_accounting(accounting_id: int):
    try:
        existing = get_accounting(accounting_id)
        if not existing:
            return None
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM accounting WHERE id = %s", (accounting_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return existing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
