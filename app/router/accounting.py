from fastapi import APIRouter, HTTPException, Query
from app.schema.accounting import accounting
from app.service.accounting import (
    get_accounting,
    get_accountings,
    get_sales_summary,
    create_accounting,
    update_accounting,
    delete_accounting,
)

router = APIRouter()


@router.get("/accounting/sales")
def read_sales(period: str = Query("all", description="all | day | week | month")):
    try:
        return get_sales_summary(period=period)
    except HTTPException as exc:
        raise exc


@router.get("/accounting")
def read_accountings():
    try:
        entries = get_accountings()
        return entries
    except HTTPException as exc:
        raise exc


@router.get("/accounting/{accounting_id}")
def read_accounting(accounting_id: int):
    try:
        entry = get_accounting(accounting_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Accounting entry not found")
        return entry
    except HTTPException as exc:
        raise exc


@router.post("/accounting")
def create_new_accounting(entry: accounting):
    try:
        new_entry = create_accounting(entry)
        return new_entry
    except HTTPException as exc:
        raise exc


@router.put("/accounting/{accounting_id}")
def update_existing_accounting(accounting_id: int, entry: accounting):
    try:
        updated_entry = update_accounting(accounting_id, entry)
        if updated_entry is None:
            raise HTTPException(status_code=404, detail="Accounting entry not found")
        return updated_entry
    except HTTPException as exc:
        raise exc


@router.delete("/accounting/{accounting_id}")
def delete_existing_accounting(accounting_id: int):
    try:
        deleted_entry = delete_accounting(accounting_id)
        if deleted_entry is None:
            raise HTTPException(status_code=404, detail="Accounting entry not found")
        return {"message": "Accounting entry deleted successfully"}
    except HTTPException as exc:
        raise exc
