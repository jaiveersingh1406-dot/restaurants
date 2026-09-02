from fastapi import APIRouter, HTTPException

from app.core.payment import create_payment_order, is_configured, verify_signature
from app.schema.order import order
from app.schema.payment import payment_init, payment_verify
from app.service.order import create_order

router = APIRouter()


@router.post("/payments/init")
def init_payment(payload: payment_init):
    try:
        if not is_configured():
            raise HTTPException(
                status_code=503,
                detail="Razorpay not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in the backend .env file.",
            )

        if not payload.amount or payload.amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid payment amount")

        result = create_payment_order(payload.amount, payload.receipt)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/verify")
def verify_payment(payload: payment_verify):
    try:
        if not is_configured():
            raise HTTPException(
                status_code=503,
                detail="Razorpay not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in the backend .env file.",
            )

        if not verify_signature(
            payload.razorpay_order_id,
            payload.payment_id,
            payload.signature,
        ):
            raise HTTPException(status_code=400, detail="Payment signature verification failed")

        # Build the order with payment details and persist it
        order_data = order(
            customer_name=payload.customer_name,
            phone=payload.phone,
            email=payload.email,
            table_no=payload.table_no,
            total=payload.total,
            status="Pending",
            payment_id=payload.payment_id,
            razorpay_order_id=payload.razorpay_order_id,
            razorpay_signature=payload.signature,
            payment_method=payload.payment_method or "Razorpay",
            payment_status="Paid",
            amount_paid=payload.total,
        )

        created = create_order(order_data)

        return {"success": True, "order": created}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))