from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/")
async def get_logs():
    try:
        with open("monitoring.log", "r") as f:
            lines = f.readlines()
        return {"logs": lines[-50:]}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")