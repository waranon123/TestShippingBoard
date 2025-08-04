# app/schemas.py - Updated for Pydantic V2
from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime
from uuid import UUID
from enum import Enum

class StatusEnum(str, Enum):
    ON_PROCESS = "On Process"
    DELAY = "Delay"
    FINISHED = "Finished"

class TruckBase(BaseModel):
    terminal: str
    truck_no: str
    dock_code: str
    truck_route: str
    preparation_start: Optional[time] = None
    preparation_end: Optional[time] = None
    loading_start: Optional[time] = None
    loading_end: Optional[time] = None
    status_preparation: StatusEnum = StatusEnum.ON_PROCESS
    status_loading: StatusEnum = StatusEnum.ON_PROCESS

class TruckCreate(TruckBase):
    pass

class TruckUpdate(BaseModel):
    terminal: Optional[str] = None
    truck_no: Optional[str] = None
    dock_code: Optional[str] = None
    truck_route: Optional[str] = None
    preparation_start: Optional[time] = None
    preparation_end: Optional[time] = None
    loading_start: Optional[time] = None
    loading_end: Optional[time] = None
    status_preparation: Optional[StatusEnum] = None
    status_loading: Optional[StatusEnum] = None

class Truck(TruckBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # Changed from orm_mode

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    
    class Config:
        from_attributes = True  # Changed from orm_mode