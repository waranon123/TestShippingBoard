from sqlalchemy import Column, String, Time, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    ON_PROCESS = "On Process"
    DELAY = "Delay"
    FINISHED = "Finished"

class Truck(Base):
    __tablename__ = "trucks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    terminal = Column(String(50), nullable=False)
    truck_no = Column(String(50), nullable=False)
    dock_code = Column(String(50), nullable=False)
    truck_route = Column(String(100), nullable=False)
    preparation_start = Column(Time, nullable=True)
    preparation_end = Column(Time, nullable=True)
    loading_start = Column(Time, nullable=True)
    loading_end = Column(Time, nullable=True)
    status_preparation = Column(SQLEnum(StatusEnum), default=StatusEnum.ON_PROCESS)
    status_loading = Column(SQLEnum(StatusEnum), default=StatusEnum.ON_PROCESS)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())