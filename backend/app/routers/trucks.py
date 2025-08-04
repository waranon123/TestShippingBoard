from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import List, Optional
from uuid import UUID

import asyncio
import json

from .config import settings
from .auth import (
    verify_password, create_access_token, get_current_user, 
    check_permission, supabase
)
from .schemas import (
    Truck, TruckCreate, TruckUpdate, Token, UserLogin,
    UserResponse, StatusEnum
)
from .websocket import manager

app = FastAPI(title="Truck Management System API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Get user from database
    result = supabase.table("users").select("*").eq("username", form_data.username).execute()
    
    if not result.data or not verify_password(form_data.password, result.data[0]["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    user = result.data[0]
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }
@app.get("/api/trucks", response_model=List[Truck])
async def get_trucks(
    skip: int = 0,
    limit: int = 100,
    terminal: Optional[str] = None,
    status_preparation: Optional[str] = None,
    status_loading: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    query = supabase.table("trucks").select("*")
    
    if terminal:
        query = query.eq("terminal", terminal)
    if status_preparation:
        query = query.eq("status_preparation", status_preparation)
    if status_loading:
        query = query.eq("status_loading", status_loading)
    
    result = query.range(skip, skip + limit - 1).execute()
    return result.data

@app.get("/api/trucks/{truck_id}", response_model=Truck)
async def get_truck(
    truck_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    result = supabase.table("trucks").select("*").eq("id", str(truck_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Truck not found")
    return result.data[0]

@app.post("/api/trucks", response_model=Truck)
async def create_truck(
    truck: TruckCreate,
    current_user: UserResponse = Depends(check_permission("user"))
):
    truck_dict = truck.dict()
    # Convert time objects to string for Supabase
    for key in ["preparation_start", "preparation_end", "loading_start", "loading_end"]:
        if truck_dict.get(key):
            truck_dict[key] = str(truck_dict[key])
    
    # Convert enum to string
    if "status_preparation" in truck_dict:
        truck_dict["status_preparation"] = truck_dict["status_preparation"].value
    if "status_loading" in truck_dict:
        truck_dict["status_loading"] = truck_dict["status_loading"].value
    
    result = supabase.table("trucks").insert(truck_dict).execute()
    
    # Broadcast update via WebSocket
    await manager.broadcast({
        "type": "truck_created",
        "data": result.data[0]
    })
    
    return result.data[0]

@app.put("/api/trucks/{truck_id}", response_model=Truck)
async def update_truck(
    truck_id: UUID,
    truck_update: TruckUpdate,
    current_user: UserResponse = Depends(check_permission("user"))
):
    update_data = truck_update.dict(exclude_unset=True)
    