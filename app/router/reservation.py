from fastapi import APIRouter, HTTPException, Query
from app.schema.reservation import reservation
from app.service.availability import get_availability
from app.service.reservation import (
    get_reservation,
    get_reservations,
    create_reservation,
    update_reservation,
    update_reservation_status,
    delete_reservation,
)

router = APIRouter()


@router.get("/reservations/availability")
def read_availability(date: str, time_slot: str):
    try:
        return get_availability(date, time_slot)
    except HTTPException as exc:
        raise exc


@router.get("/reservations")
def read_reservations(status: str = Query(None, description="Filter by status")):
    try:
        entries = get_reservations(status=status)
        return entries
    except HTTPException as exc:
        raise exc


@router.get("/reservations/{reservation_id}")
def read_reservation(reservation_id: int):
    try:
        entry = get_reservation(reservation_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return entry
    except HTTPException as exc:
        raise exc


@router.post("/reservations")
def create_new_reservation(entry: reservation):
    try:
        new_entry = create_reservation(entry)
        return new_entry
    except HTTPException as exc:
        raise exc


@router.put("/reservations/{reservation_id}/status")
def update_reservation_status_endpoint(reservation_id: int, status: str):
    try:
        if status not in ("Pending", "Confirmed", "Waiting", "Cancelled", "Completed"):
            raise HTTPException(status_code=400, detail="Invalid status")
        return update_reservation_status(reservation_id, status)
    except HTTPException as exc:
        raise exc


@router.put("/reservations/{reservation_id}")
def update_existing_reservation(reservation_id: int, entry: reservation):
    try:
        updated_entry = update_reservation(reservation_id, entry)
        if updated_entry is None:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return updated_entry
    except HTTPException as exc:
        raise exc
        raise exc


@router.delete("/reservations/{reservation_id}")
def delete_existing_reservation(reservation_id: int):
    try:
        deleted_entry = delete_reservation(reservation_id)
        if deleted_entry is None:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"message": "Reservation deleted successfully"}
    except HTTPException as exc:
        raise exc
