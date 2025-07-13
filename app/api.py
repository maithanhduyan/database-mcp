# -*- coding: utf-8 -*-
# File: app/api.py

from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def api_root():
    """API root endpoint for the application."""
    return {"status": "ok", "message": "Welcome to the Postgres MCP Service!"}
