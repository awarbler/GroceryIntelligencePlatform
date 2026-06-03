# =============================================================================
# File: backend/scripts/create_dev_user.py
# Project: Grocery Intelligence Platform
# Description: Creates one local development user with a bcrypt-hashed password.
# Author: Anita Woodford
# SRS Traceability: Supports SRS v5.0 Section 2 U-001 and U-004.
# SDD Traceability: Supports SDD v5.0 Section 10.1 Authentication.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

import asyncio  # Runs async database code from this script.

from backend.data_access.users import create_user, get_user_by_username  # Uses existing user DAL helpers.
from backend.database import connect_to_mongodb, disconnect_from_mongodb, get_db  # Uses existing database helpers.
from backend.models.user import UserModel  # Uses existing user model validation.
from backend.services.auth_service import hash_password  # Uses existing bcrypt hash helper.


async def create_dev_user() -> None:  # Defines the async dev-user creation workflow.
    await connect_to_mongodb()  # Opens the MongoDB connection using the project database setup.

    try:  # Ensures the database connection is closed after the script runs.
        db = get_db()  # Gets the active MongoDB database instance.

        username = "anita"  # Defines the local development username.
        password = "ChangeMe123!"  # Defines the local development password.

        existing_user = await get_user_by_username(db, username)  # Checks whether this username already exists.

        if existing_user is not None:  # Prevents duplicate user documents.
            print("User already exists: anita")  # Prints a safe status message.
            return  # Stops the script.

        user_model = UserModel(  # Builds a validated user document.
            username=username,  # Sets the username.
            password_hash=hash_password(password),  # Stores only the hashed password.
            preferred_stores=["heb"],  # Adds H-E-B as the Phase 1 default store.
        )  # Ends user model creation.

        inserted_id = await create_user(  # Inserts the user through the existing DAL helper.
            db,  # Passes the active MongoDB database.
            user_model.model_dump(by_alias=True, mode="json"),  # Converts the model into a MongoDB-ready dictionary.
        )  # Ends insert call.

        print(f"Created local dev user with id: {inserted_id}")  # Prints inserted user id.
        print("Username: anita")  # Prints local username.
        print("Temporary password: ChangeMe123!")  # Prints local temporary password.
    finally:  # Runs cleanup after success or failure.
        await disconnect_from_mongodb()  # Closes the MongoDB connection.


if __name__ == "__main__":  # Runs only when executed directly.
    asyncio.run(create_dev_user())  # Starts the async script.