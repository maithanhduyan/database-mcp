# -*- coding: utf-8 -*-
# File: app/main.py

from sqlalchemy import text
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from app.logger import get_logger
from app.db import get_db,init_db
from app.api import router as api_router
from app.mcp import router as mcp_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # App Startup
    try:
        # Initialize all databases (users + MCP tables)
        await asyncio.to_thread(init_db)
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
    
    yield
    
    # App Shutdown
    try:
        logger.info("Application shutting down")
    except Exception as e:
        logger.error(f"Failed to shut down application: {e}")


app = FastAPI(lifespan=lifespan)

app.include_router(
    api_router,  # Import the API router from the app.api module
    prefix="/api",  # Set a prefix for all routes in this router
    tags=["api"]  # Tag for grouping in the OpenAPI documentation
)

app.include_router(
    mcp_router,  # Import the MCP router from the app.mcp module
    prefix="/mcp",  # Set a prefix for all routes in this router
    tags=["mcp"]  # Tag for grouping in the OpenAPI documentation
)

def main() -> None:
    """
    Hàm main kiểm tra kết nối và truy vấn dữ liệu mẫu.
    """

    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()