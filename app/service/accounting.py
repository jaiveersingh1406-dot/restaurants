from datetime import date, timedelta

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
    """Automatically compute revenue and order counts from real order rows.

    period filter (day/week/month) is based on the order's created_at date.
    Expenses come from manually entered accounting entries.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        order_where = ""
        order_params = ()
        if period in ("day", "week", "month"):
            cutoff = None
            if period == "day":
                cutoff = date.today()
            elif period == "week":
                cutoff = date.today() - timedelta(days=7)
            elif period == "month":
                cutoff = date.today() - timedelta(days=30)
            order_where = "WHERE created_at >= %s"
            order_params = (cutoff,)

        # Real revenue + orders from the orders table
        cursor.execute(
            f"""SELECT
                    COUNT(*) AS total_orders,
                    COALESCE(SUM(amount_paid), 0) AS total_revenue,
                    COALESCE(SUM(total), 0) AS order_value
                FROM orders {order_where}""",
            order_params,
        )
        stats = cursor.fetchone()
        total_orders = int(stats["total_orders"])
        total_revenue = float(stats["total_revenue"])

        # Manual expenses from accounting entries
        cursor.execute("SELECT COALESCE(SUM(expenses), 0) AS total_expenses FROM accounting")
        total_expenses = float(cursor.fetchone()["total_expenses"])

        # Recent order rows for reference
        rows = _fetch_all(
            cursor,
            "SELECT * FROM orders " + order_where + " ORDER BY id DESC",
            order_params if order_params else None,
        )[:30]

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
               VALUES (%s, %s, %s, %s)
               RETURNING id""",
            (
                accounting_data.day,
                accounting_data.revenue,
                accounting_data.expenses,
                accounting_data.orders
            )
        )

        connection.commit()
        accounting_id = cursor.fetchone()[0]

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
