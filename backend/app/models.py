from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, nullable=False, unique=True, index=True)
    status = Column(String, nullable=False, default="AVAILABLE")  # AVAILABLE/RESERVED/OUT
    mileage = Column(Integer, nullable=False, default=0)
    location = Column(String, nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=True)

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="RESERVED")  # RESERVED/OUT/COMPLETED

    # checkout/checkin fields (minimal audit)
    mileage_out = Column(Integer, nullable=True)
    mileage_in = Column(Integer, nullable=True)
    checkin_notes = Column(String, nullable=True)

    customer = relationship("Customer")
    vehicle = relationship("Vehicle")
    agreement = relationship("Agreement", uselist=False, back_populates="reservation")

class Agreement(Base):
    __tablename__ = "agreements"
    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False, unique=True)
    signed_by = Column(String, nullable=True)
    signed_at = Column(DateTime, nullable=True)

    reservation = relationship("Reservation", back_populates="agreement")
