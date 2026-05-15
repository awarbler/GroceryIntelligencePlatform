# =============================================================================
# File: test_no_mongo_crud_in_services.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Verifies that service modules do not perform direct MongoDB CRUD.
# Security Note: Static architecture tests enforce the service to Data Access Layer boundary.
# SRS Traceability: Supports SRS v5.0 SE-009.
# SDD Traceability: Supports SDD v5.0 service layer and database access separation.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

from pathlib import Path  # Imports Path for filesystem scanning.


FORBIDDEN_SERVICE_PATTERNS = [  # Lists MongoDB CRUD patterns forbidden in service files.
    ".find_one(",  # Blocks direct MongoDB find_one usage in services.
    ".insert_one(",  # Blocks direct MongoDB insert_one usage in services.
    ".update_one(",  # Blocks direct MongoDB update_one usage in services.
    ".delete_one(",  # Blocks direct MongoDB delete_one usage in services.
    "AsyncIOMotorClient",  # Blocks service-level MongoDB client creation.
]  # Ends the forbidden service pattern list.


def test_services_do_not_call_mongodb_crud_directly() -> (
    None
):  # Tests service files for direct MongoDB CRUD.
    services_path = Path(
        "backend/services"
    )  # Points to the backend services directory.

    if not services_path.exists():  # Checks whether service files exist yet.
        return  # Allows the test to pass before service files exist.

    violations: list[str] = []  # Stores detected architecture violations.

    for service_file in services_path.rglob(
        "*.py"
    ):  # Loops through every service Python file.
        file_text = service_file.read_text(
            encoding="utf-8"
        )  # Reads the service file content.

        for (
            pattern
        ) in FORBIDDEN_SERVICE_PATTERNS:  # Loops through forbidden service patterns.
            if (
                pattern in file_text
            ):  # Checks whether the service file contains the pattern.
                violations.append(
                    f"{service_file}: contains {pattern}"
                )  # Records the violation.

    assert (
        violations == []
    )  # Fails the test if any service performs direct MongoDB CRUD.
