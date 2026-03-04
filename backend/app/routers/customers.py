from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    c = Customer(name=payload.name, contact=payload.contact)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.id.asc()).all()

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return c
