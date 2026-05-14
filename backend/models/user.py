# =============================================================================
# File: user.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines user preference and reporting models for the Grocery Intelligence Platform.
# Security Note: Stores password hashes only and does not store plaintext passwords.
# SRS Traceability: Supports SRS v5.0 user preferences, report output, OCR review thresholds, and reward valuation settings.
# SDD Traceability: Supports SDD v5.0 backend model validation and user configuration design.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from decimal import Decimal  # Imports Decimal for exact money and point conversion values.

from enum import StrEnum  # Imports StrEnum so enum values behave like strings.

from pydantic import Field  # Imports Field for validation constraints and default values.

from backend.models.base import BaseDocument  # Imports the shared MongoDB document base model.


class ReportFormat(StrEnum):  # Defines supported report output formats.
    """Enum representing supported report export formats."""  # Documents the purpose of the enum.

    PDF = "PDF"  # Allows users to export reports as PDF files.
    CSV = "CSV"  # Allows users to export reports as CSV files.
    JSON = "JSON"  # Allows users to export reports as JSON data.


class UserModel(BaseDocument):  # Defines the user preference model stored in MongoDB.
    """Model representing user account preferences and reporting settings."""  # Documents the purpose of the model.

    username: str = Field(..., min_length=1)  # Stores the user's login or display username.
    password_hash: str = Field(..., min_length=1)  # Stores the hashed password and never the plaintext password.
    preferred_stores: list[str] = Field(default_factory=list)  # Stores the user's preferred grocery or coupon stores.
    report_format: ReportFormat = Field(default=ReportFormat.PDF)  # Stores the user's default report output format.
    ocr_threshold_review: float = Field(default=0.75, ge=0.0, le=1.0)  # Stores the confidence value below which OCR needs human review.
    ocr_threshold_accept: float = Field(default=0.95, ge=0.0, le=1.0)  # Stores the confidence value at or above which OCR can be accepted automatically.
    fetch_points_per_dollar: Decimal = Field(default=Decimal("1000.00"), ge=Decimal("0.00"))  # Stores the Fetch point conversion rate.