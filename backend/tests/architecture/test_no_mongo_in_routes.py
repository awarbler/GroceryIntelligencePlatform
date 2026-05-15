# =============================================================================
# File: test_no_mongo_in_routes.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Verifies that API route handlers do not contain direct MongoDB access.
# Security Note: Static architecture tests prevent route handlers from bypassing validation.
# SRS Traceability: Supports SRS v5.0 SE-009.
# SDD Traceability: Supports SDD v5.0 API route and service layer separation.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

from pathlib import Path  # Imports Path for filesystem scanning.


FORBIDDEN_ROUTE_PATTERNS = [  # Lists MongoDB access patterns forbidden in route files.
    ".find_one(",  # Blocks direct MongoDB find_one usage in routes.
    ".find(",  # Blocks direct MongoDB find usage in routes.
    ".insert_one(",  # Blocks direct MongoDB insert_one usage in routes.
    ".update_one(",  # Blocks direct MongoDB update_one usage in routes.
    ".delete_one(",  # Blocks direct MongoDB delete_one usage in routes.
    "AsyncIOMotorClient",  # Blocks route-level MongoDB client creation.
    "get_database(",  # Blocks direct database dependency use in routes.
]  # Ends the forbidden route pattern list.


def test_api_routes_do_not_query_mongodb_directly() -> (
    None
):  # Tests route files for direct MongoDB access.
    api_path = Path("backend/api")  # Points to the backend API route directory.

    if not api_path.exists():  # Checks whether API routes exist yet.
        return  # Allows the test to pass before route files exist.

    violations: list[str] = []  # Stores detected architecture violations.

    for route_file in api_path.rglob("*.py"):  # Loops through every route Python file.
        file_text = route_file.read_text(
            encoding="utf-8"
        )  # Reads the route file content.

        for (
            pattern
        ) in FORBIDDEN_ROUTE_PATTERNS:  # Loops through forbidden route patterns.
            if (
                pattern in file_text
            ):  # Checks whether the route file contains the pattern.
                violations.append(
                    f"{route_file}: contains {pattern}"
                )  # Records the violation.

    assert (
        violations == []
    )  # Fails the test if any route handler queries MongoDB directly.
