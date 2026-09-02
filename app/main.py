import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.db import get_connection

load_dotenv()
from app.router.auth import router as auth_router
from app.router.product import router as product_router
from app.router.accounting import router as accounting_router
from app.router.reservation import router as reservation_router
from app.router.dashboard import router as dashboard_router
from app.router.order import router as order_router
from app.router.content import router as content_router
from app.router.payment import router as payment_router


app = FastAPI()
CROSS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CROSS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/menu")
def get_menu():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM menu")
        menu_items = cursor.fetchall()
        return menu_items
    finally:
        cursor.close()
        connection.close()


@app.get("/menu/{item_id}")
def get_menu_item(item_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM menu WHERE id = %s", (item_id,))
        menu_item = cursor.fetchone()
        return menu_item
    finally:
        cursor.close()
        connection.close()


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(accounting_router)
app.include_router(reservation_router)
app.include_router(dashboard_router)
app.include_router(order_router)
app.include_router(content_router)
app.include_router(payment_router)
