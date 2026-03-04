from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Reservation, Vehicle, Customer, Agreement
from ..schemas import ReservationCreate, ReservationOut, CheckoutIn, CheckinIn, SignIn, AgreementOut
from ..services.overlap import intervals_overlap

router = APIRouter(prefix="/reservations", tags=["reservations"])

def _get_reservation(db: Session, reservation_id: int) -> Reservation:
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Reservation not found.")
    return r

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

    # Keep vehicle status in sync (simple state model)
    vehicle.status = "RESERVED"

    db.commit()
    db.refresh(res)
    return res

@router.get("", response_model=list[ReservationOut])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.id.asc()).all()

@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return _get_reservation(db, reservation_id)

@router.post("/{reservation_id}/checkout", response_model=ReservationOut)
def checkout(reservation_id: int, payload: CheckoutIn, db: Session = Depends(get_db)):
    r = _get_reservation(db, reservation_id)
    if r.status != "RESERVED":
        raise HTTPException(status_code=409, detail="Reservation must be RESERVED to checkout.")

    v = db.query(Vehicle).filter(Vehicle.id == r.vehicle_id).first()
    if v is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    if payload.mileage_out < v.mileage:
        raise HTTPException(status_code=422, detail="mileage_out cannot be less than current vehicle mileage.")

    r.mileage_out = payload.mileage_out
    r.status = "OUT"
    v.mileage = payload.mileage_out
    v.status = "OUT"

    db.commit()
    db.refresh(r)
    return r

@router.post("/{reservation_id}/checkin", response_model=ReservationOut)
def checkin(reservation_id: int, payload: CheckinIn, db: Session = Depends(get_db)):
    r = _get_reservation(db, reservation_id)
    if r.status != "OUT":
        raise HTTPException(status_code=409, detail="Reservation must be OUT to checkin.")

    v = db.query(Vehicle).filter(Vehicle.id == r.vehicle_id).first()
    if v is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    if r.mileage_out is not None and payload.mileage_in < r.mileage_out:
        raise HTTPException(status_code=422, detail="mileage_in cannot be less than mileage_out.")
    if payload.mileage_in < v.mileage:
        raise HTTPException(status_code=422, detail="mileage_in cannot be less than current vehicle mileage.")

    r.mileage_in = payload.mileage_in
    r.checkin_notes = payload.notes
    r.status = "COMPLETED"
    v.mileage = payload.mileage_in
    v.status = "AVAILABLE"

    db.commit()
    db.refresh(r)
    return r

@router.post("/{reservation_id}/sign", response_model=AgreementOut)
def sign_agreement(reservation_id: int, payload: SignIn, db: Session = Depends(get_db)):
    r = _get_reservation(db, reservation_id)

    ag = db.query(Agreement).filter(Agreement.reservation_id == r.id).first()
    if ag is None:
        ag = Agreement(reservation_id=r.id)
        db.add(ag)

    ag.signed_by = payload.signed_by
    ag.signed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ag)
    return ag
