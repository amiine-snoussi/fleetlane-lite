from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Vehicle
from ..schemas import VehicleCreate, VehicleOut

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("", response_model=VehicleOut, status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    v = Vehicle(plate=payload.plate, mileage=payload.mileage, location=payload.location, status="AVAILABLE")
    db.add(v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vehicle plate already exists.")
    db.refresh(v)
    return v

@router.get("", response_model=list[VehicleOut])
def list_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).order_by(Vehicle.id.asc()).all()
