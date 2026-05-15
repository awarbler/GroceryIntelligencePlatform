# =============================================================================
# File: test_data_access_structure.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Verifies that all required Phase 1 Data Access Layer modules import.
# Security Note: This test does not connect to MongoDB and does not use secrets.
# SRS Traceability: Supports SRS v5.0 SE-009 and Section 19 database schema.
# SDD Traceability: Supports SDD v5.0 backend folder structure and database design.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

import importlib  # Imports importlib so tests can import modules by string name.


REQUIRED_DATA_ACCESS_MODULES = [  # Lists every required Phase 1 data access module.
    "backend.data_access.base",  # Requires the shared base module.
    "backend.data_access.users",  # Requires the users collection module.
    "backend.data_access.stores",  # Requires the stores collection module.
    "backend.data_access.products",  # Requires the products collection module.
    "backend.data_access.purchases",  # Requires the purchases collection module.
    "backend.data_access.ads",  # Requires the ads collection module.
    "backend.data_access.coupons",  # Requires the coupons collection module.
    "backend.data_access.rebates",  # Requires the rebates collection module.
    "backend.data_access.reward_accounts",  # Requires the reward accounts collection module.
    "backend.data_access.reward_transactions",  # Requires the reward transactions collection module.
    "backend.data_access.deal_matches",  # Requires the deal matches collection module.
    "backend.data_access.raw_inputs",  # Requires the raw inputs collection module.
]  # Ends the required module list.


def test_required_data_access_modules_import() -> (
    None
):  # Tests that all required modules import.
    for (
        module_name
    ) in REQUIRED_DATA_ACCESS_MODULES:  # Loops over each required module name.
        imported_module = importlib.import_module(
            module_name
        )  # Imports the module dynamically.
        assert imported_module is not None  # Verifies the import succeeded.
