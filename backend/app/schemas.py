from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator

# ---------- Vehicles ----------
class VehicleCreate(BaseModel):
    plate: str
    mileage: int = 0
    location: str | None = None

class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plate: str
    status: str
    mileage: int
    location: str | None = None

# ---------- Customers ----------
class CustomerCreate(BaseModel):
    name: str
    contact: str | None = None

class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    contact: str | None = None

# ---------- Reservations ----------
class ReservationCreate(BaseModel):
    customer_id: int
    vehicle_id: int
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def _validate_interval(self):
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be before end_at")
        return self

class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    vehicle_id: int
    start_at: datetime
    end_at: datetime
    status: str
    mileage_out: int | None = None
    mileage_in: int | None = None
    checkin_notes: str | None = None

# ---------- Actions ----------
class CheckoutIn(BaseModel):
    mileage_out: int

class CheckinIn(BaseModel):
    mileage_in: int
    notes: str | None = None

class SignIn(BaseModel):
    signed_by: str

class AgreementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    reservation_id: int
    signed_by: str | None = None
    signed_at: datetime | None = None
