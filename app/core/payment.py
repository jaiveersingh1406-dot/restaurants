import hashlib
import hmac
import os

import razorpay

CURRENCY = "INR"


def _keys():
    return {
        "key_id": os.environ.get("RAZORPAY_KEY_ID", "").strip(),
        "key_secret": os.environ.get("RAZORPAY_KEY_SECRET", "").strip(),
    }


def is_configured() -> bool:
    k = _keys()
    return bool(k["key_id"]) and bool(k["key_secret"])


def public_key_id() -> str:
    return _keys()["key_id"]


def _client() -> razorpay.Client:
    k = _keys()
    return razorpay.Client(auth=(k["key_id"], k["key_secret"]))


def create_payment_order(amount_inr: float, receipt: str = None) -> dict:
    """Create a Razorpay order. amount is in INR (converted to paise)."""
    if not is_configured():
        raise RuntimeError(
            "Razorpay not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in the backend .env file."
        )

    data = {
        "amount": int(round(amount_inr * 100)),  # paise
        "currency": CURRENCY,
        "receipt": receipt or "",
        "notes": {"source": "platia-web"},
    }

    result = _client().order.create(data=data)
    return {
        "id": result["id"],
        "amount": result["amount"],       # paise
        "amount_inr": result["amount"] / 100.0,
        "currency": result["currency"],
        "status": result["status"],
        "key_id": public_key_id(),
    }


def verify_signature(razorpay_order_id: str, razorpay_payment_id: str, signature: str) -> bool:
    """Verify the Razorpay payment signature with the API secret."""
    k = _keys()
    message = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    expected = hmac.new(k["key_secret"].encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)