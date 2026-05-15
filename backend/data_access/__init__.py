# =============================================================================
# File: __init__.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Exports approved Phase 1 Data Access Layer classes.
# Security Note: Centralizes MongoDB access so route handlers do not query MongoDB directly.
# SRS Traceability: Supports SRS v5.0 SE-009 and Section 19 database schema.
# SDD Traceability: Supports SDD v5.0 backend folder structure and database design.
# =============================================================================

from backend.data_access.ads import AdsDataAccess  # Exports ad document data access.
from backend.data_access.base import (
    DataAccessError,
)  # Exports the shared data access exception.
from backend.data_access.base import MongoDataAccess  # Exports the shared CRUD helper.
from backend.data_access.base import (
    normalize_object_id,
)  # Exports the ObjectId validation helper.
from backend.data_access.coupons import (
    CouponsDataAccess,
)  # Exports coupon document data access.
from backend.data_access.deal_matches import (
    DealMatchesDataAccess,
)  # Exports deal match document data access.
from backend.data_access.products import (
    ProductsDataAccess,
)  # Exports product document data access.
from backend.data_access.purchases import (
    PurchasesDataAccess,
)  # Exports purchase document data access.
from backend.data_access.raw_inputs import (
    RawInputsDataAccess,
)  # Exports raw input document data access.
from backend.data_access.rebates import (
    RebatesDataAccess,
)  # Exports rebate document data access.
from backend.data_access.reward_accounts import (
    RewardAccountsDataAccess,
)  # Exports reward account document data access.
from backend.data_access.reward_transactions import (
    RewardTransactionsDataAccess,
)  # Exports reward transaction data access.
from backend.data_access.stores import (
    StoresDataAccess,
)  # Exports store document data access.
from backend.data_access.users import (
    UsersDataAccess,
)  # Exports user document data access.

__all__ = [  # Defines the public exports for this package.
    "AdsDataAccess",  # Allows controlled import of AdsDataAccess.
    "CouponsDataAccess",  # Allows controlled import of CouponsDataAccess.
    "DataAccessError",  # Allows controlled import of DataAccessError.
    "DealMatchesDataAccess",  # Allows controlled import of DealMatchesDataAccess.
    "MongoDataAccess",  # Allows controlled import of MongoDataAccess.
    "ProductsDataAccess",  # Allows controlled import of ProductsDataAccess.
    "PurchasesDataAccess",  # Allows controlled import of PurchasesDataAccess.
    "RawInputsDataAccess",  # Allows controlled import of RawInputsDataAccess.
    "RebatesDataAccess",  # Allows controlled import of RebatesDataAccess.
    "RewardAccountsDataAccess",  # Allows controlled import of RewardAccountsDataAccess.
    "RewardTransactionsDataAccess",  # Allows controlled import of RewardTransactionsDataAccess.
    "StoresDataAccess",  # Allows controlled import of StoresDataAccess.
    "UsersDataAccess",  # Allows controlled import of UsersDataAccess.
    "normalize_object_id",  # Allows controlled import of normalize_object_id.
]
