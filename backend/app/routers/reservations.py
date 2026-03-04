from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Reservation, Vehicle, Customer
from ..schemas import ReservationCreate, ReservationOut
from ..services.overlap import intervals_overlap

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found.")

    existing = (
        db.query(Reservation)
        .filter(Reservation.vehicle_id == payload.vehicle_id)
        .filter(Reservation.status != "COMPLETED")
        .all()
    )

    for r in existing:
        if intervals_overlap(r.start_at, r.end_at, payload.start_at, payload.end_at):
            raise HTTPException(status_code=409, detail="Vehicle already reserved for that interval.")

    res = Reservation(
        customer_id=payload.customer_id,
        vehicle_id=payload.vehicle_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        status="RESERVED",
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    return res

@router.get("", response_model=list[ReservationOut])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.id.asc()).all()
