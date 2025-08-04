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
@app.get("/api/stats")
async def get_statistics(current_user: UserResponse = Depends(get_current_user)):
    # Get all trucks
    result = supabase.table("trucks").select("*").execute()
    trucks = result.data
    
    # Calculate statistics
    total_trucks = len(trucks)
    
    preparation_stats = {
        "On Process": sum(1 for t in trucks if t["status_preparation"] == "On Process"),
        "Delay": sum(1 for t in trucks if t["status_preparation"] == "Delay"),
        "Finished": sum(1 for t in trucks if t["status_preparation"] == "Finished")
    }
    
    loading_stats = {
        "On Process": sum(1 for t in trucks if t["status_loading"] == "On Process"),
        "Delay": sum(1 for t in trucks if t["status_loading"] == "Delay"),
        "Finished": sum(1 for t in trucks if t["status_loading"] == "Finished")
    }
    
    # Terminal statistics
    terminal_stats = {}
    for truck in trucks:
        terminal = truck["terminal"]
        if terminal not in terminal_stats:
            terminal_stats[terminal] = 0
        terminal_stats[terminal] += 1
    
    return {
        "total_trucks": total_trucks,
        "preparation_stats": preparation_stats,
        "loading_stats": loading_stats,
        "terminal_stats": terminal_stats,
        "last_updated": datetime.utcnow().isoformat()
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back or handle any client messages if needed
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

        