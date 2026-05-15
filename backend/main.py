# =============================================================================
# File: main.py
# Project: GroceryIntelligence Platform
# Author: Anita Woodford
# Purpose: FASTAPI application entry point for backend API service
# Descriptions: This file creates the FastAPI application instance, defines API routes, and
# includes startup and shutdown event handlers for database connection management.
# Security Note:
#
# =============================================================================
from __future__ import annotations  # Enables modern type annotation behavior.
from collections.abc import AsyncGenerator# Imports the AsyncGenerator type for defining async generator functions.
from contextlib import asynccontextmanager # Imports the asynccontextmanager decorator for creating async context managers.

from fastapi import FastAPI # Imports the FastAPI class used to create the backend application.
from slowapi.middleware import SlowAPIMiddleware  # Imports SlowAPI middleware so rate limits are enforced.

from backend.api.routes import register_routes  # Imports central API route registration.
from backend.data_access.token_denylist import ensure_token_denylist_indexes  # Imports token denylist index creation.
from backend.database import connect_to_mongodb  # Imports MongoDB startup connection logic.
from backend.database import disconnect_from_mongodb  # Imports MongoDB shutdown disconnection logic.
from backend.database import get_db  # Imports the active MongoDB database accessor.

@asynccontextmanager  # Decorates the lifespan function to manage application startup and shutdown.
async def lifespan(app: FastAPI,) -> AsyncGenerator[None, None]:  # Defines an async context manager function for managing the application's lifespan.
    await connect_to_mongodb()  # Connects to MongoDB when the application starts up.
    await ensure_token_denylist_indexes(get_db())  # Ensures token denylist indexes exist at startup.
    yield  # Yields control back to the application to run normally.
    await (disconnect_from_mongodb())  # Disconnects from MongoDB when the application is shutting down.


app = FastAPI(lifespan=lifespan)  # Creates the FastAPI application with existing lifespan management.
app.add_middleware(SlowAPIMiddleware)  # Enables SlowAPI rate-limit enforcement.
register_routes(app)  # Registers API routers and rate-limit exception handling.

@app.get("/")  # Defines a test route for the backend root URL.
def read_root():  # Creates the function that runs when someone visits the root URL.
    return {"message": "Grocery Intelligence Platform API is running"}  # Sends a simple JSON response so we know the API works.
