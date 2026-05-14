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

from collections.abc import AsyncGenerator  # Imports the AsyncGenerator type for defining async generator functions.
from contextlib import asynccontextmanager  # Imports the asynccontextmanager decorator for creating async context managers.

from fastapi import FastAPI  # Imports the FastAPI class used to create the backend application.
from backend.database import connect_to_mongodb, disconnect_from_mongodb  # Imports the database connection management functions from the database module.

@asynccontextmanager  # convert the function into a fastapi lifespan 
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # Defines an async context manager function for managing the application's lifespan.
    await connect_to_mongodb()  # Connects to MongoDB when the application starts up.
    yield  # Yields control back to the application to run normally.
    await disconnect_from_mongodb()  # Disconnects from MongoDB when the application is shutting down.

app = FastAPI(lifespan=lifespan)  # Creates the FastAPI application object that Uvicorn needs to run.

@app.get("/")  # Defines a test route for the backend root URL.
def read_root():  # Creates the function that runs when someone visits the root URL.
    return {"message": "Grocery Intelligence Platform API is running"}  # Sends a simple JSON response so we know the API works.