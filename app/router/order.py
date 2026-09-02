from fastapi import APIRouter, HTTPException, Query
from app.schema.order import order
from app.service.order import (
    get_order,
    get_orders,
    create_order,
    update_order_status,
    delete_order,
)

router = APIRouter()


@router.get("/orders")
def read_orders(
    status: str = Query(None, description="Filter by order status"),
    payment_status: str = Query(None, description="Filter by payment status"),
):
    try:
        return get_orders(status=status, payment_status=payment_status)
    except HTTPException as exc:
        raise exc


@router.get("/orders/{order_id}")
def read_order(order_id: int):
    try:
        entry = get_order(order_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return entry
    except HTTPException as exc:
        raise exc


@router.post("/orders")
def place_order(payload: order):
    try:
        if not payload.customer_name or not payload.total:
            raise HTTPException(status_code=400, detail="Order must have a customer name and total")

        return create_order(payload)
    except HTTPException as exc:
        raise exc


@router.put("/orders/{order_id}/status")
def change_status(order_id: int, status: str):
    try:
        if status not in ("Pending", "Preparing", "Completed", "Cancelled"):
            raise HTTPException(status_code=400, detail="Invalid status")
        return update_order_status(order_id, status)
    except HTTPException as exc:
        raise exc


@router.delete("/orders/{order_id}")
def remove_order(order_id: int):
    try:
        deleted = delete_order(order_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order deleted successfully"}
    except HTTPException as exc:
        raise exc
