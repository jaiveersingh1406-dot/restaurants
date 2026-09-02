from datetime import date, datetime, timedelta

from fastapi import HTTPException

from app.db.db import get_connection


def _fetch_one(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchone()


def _resolve_period(period):
    """Return (label, cutoff_date_or_datetime, cutoff_string) for the filter.

    all -> no filter, returns (None, None, None)
    """
    period = (period or "all").lower()
    today = date.today()

    if period == "day":
        cutoff = today
        label = "Today"
    elif period == "week":
        cutoff = today - timedelta(days=7)
        label = "Last 7 Days"
    elif period == "month":
        cutoff = today - timedelta(days=30)
        label = "Last 30 Days"
    else:
        return None, None, None, period

    # created_at is a timestamp so compare against start-of-day for "day"
    if period == "day":
        cutoff_dt = datetime.combine(cutoff, datetime.min.time())
        cutoff_str = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        cutoff_dt = cutoff
        cutoff_str = cutoff.strftime("%Y-%m-%d")

    return label, cutoff_dt, cutoff_str, period


def get_dashboard_stats(period="all"):
    label, cutoff_dt, cutoff_str, period = _resolve_period(period)

    order_where = "WHERE created_at >= %s" if cutoff_str else ""
    order_params = (cutoff_str,) if cutoff_str else ()

    reservation_where = "WHERE reservation_date >= %s" if cutoff_str else ""
    reservation_params = (cutoff_str,) if cutoff_str else ()

    accounting_where = "WHERE day >= %s" if cutoff_str else ""
    accounting_params = (cutoff_str,) if cutoff_str else ()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # ===== KPI COUNTS =====
        order_stats = _fetch_one(
            cursor,
            f"""SELECT COUNT(*) AS total_orders,
                       COALESCE(SUM(CASE WHEN payment_status = 'Paid' THEN amount_paid END), 0) AS revenue,
                       COALESCE(SUM(total), 0) AS order_value
                FROM orders {order_where}""",
            order_params,
        )
        total_orders = order_stats["total_orders"]
        revenue = float(order_stats["revenue"]) if order_stats["revenue"] else 0.0

        reservations_count = _fetch_one(
            cursor,
            f"SELECT COUNT(*) AS c FROM reservations {reservation_where}",
            reservation_params,
        )["c"]
        customers_count = _fetch_one(cursor, "SELECT COUNT(*) AS c FROM users")["c"]
        menu_count = _fetch_one(cursor, "SELECT COUNT(*) AS c FROM menu")["c"]

        product_stats = _fetch_one(
            cursor,
            """SELECT COUNT(*) AS total_products,
                      COALESCE(SUM(stock), 0) AS total_stock,
                      SUM(CASE WHEN stock <= 10 THEN 1 ELSE 0 END) AS low_stock
               FROM product""",
        )
        total_products = product_stats["total_products"]
        total_stock = product_stats["total_stock"]
        low_stock = product_stats["low_stock"] or 0

        # ===== ACCOUNTING =====
        accounting = _fetch_one(
            cursor,
            f"""SELECT COALESCE(SUM(revenue), 0) AS revenue,
                       COALESCE(SUM(expenses), 0) AS expenses,
                       COALESCE(SUM(orders), 0) AS accounting_orders
                FROM accounting {accounting_where}""",
            accounting_params,
        )
        accounting_revenue = float(accounting["revenue"])
        expenses = float(accounting["expenses"])
        profit = accounting_revenue - expenses

        # ===== ORDERS BY STATUS =====
        cursor.execute(
            f"SELECT status, COUNT(*) AS count FROM orders {order_where} GROUP BY status",
            order_params,
        )
        orders_by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

        # ===== PAYMENT BREAKDOWN =====
        cursor.execute(
            f"""SELECT payment_status, COUNT(*) AS count
                FROM orders {order_where} GROUP BY payment_status""",
            order_params,
        )
        payment_breakdown = {
            (row["payment_status"] or "Unpaid"): row["count"]
            for row in cursor.fetchall()
        }

        # ===== RECENT ORDERS =====
        cursor.execute(f"SELECT * FROM orders {order_where} ORDER BY id DESC LIMIT 6", order_params)
        recent_orders = cursor.fetchall()

        # ===== RECENT RESERVATIONS =====
        cursor.execute(
            f"""SELECT id, customer_name, table_no, time_slot, reservation_date, status
                FROM reservations {reservation_where} ORDER BY id DESC LIMIT 5""",
            reservation_params,
        )
        recent_reservations = cursor.fetchall()

        # ===== INVENTORY (low stock first) =====
        cursor.execute(
            "SELECT id, name, stock, status FROM product ORDER BY stock ASC LIMIT 6"
        )
        inventory = cursor.fetchall()

        # ===== PERFORMANCE: revenue by day (accounting) =====
        cursor.execute(
            f"SELECT day, SUM(revenue) AS revenue FROM accounting {accounting_where} GROUP BY day ORDER BY MIN(id) ASC",
            accounting_params,
        )
        performance = [
            {"day": row["day"], "revenue": float(row["revenue"])}
            for row in cursor.fetchall()
        ]

        cursor.close()
        connection.close()

        return {
            # Period info
            "period": period,
            "period_label": label,
            # KPIs
            "total_orders": total_orders,
            "reservations_count": reservations_count,
            "revenue_total": revenue,
            "order_value_total": float(order_stats["order_value"] or 0),
            "customers_count": customers_count,
            "menu_count": menu_count,
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock_count": low_stock,
            # Accounting
            "accounting_revenue": accounting_revenue,
            "expenses": expenses,
            "profit": profit,
            "accounting_orders": accounting["accounting_orders"],
            # Breakdowns
            "orders_by_status": orders_by_status,
            "payment_breakdown": payment_breakdown,
            "payment_breakdown_total": sum(payment_breakdown.values()),
            # Lists
            "recent_orders": recent_orders,
            "recent_reservations": recent_reservations,
            "inventory": inventory,
            "performance": performance,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
