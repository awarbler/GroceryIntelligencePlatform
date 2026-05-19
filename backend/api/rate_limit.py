# =============================================================================
# File: api/rate_limit.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides the shared FastAPI rate limiter instance.
# Security Note: Used to slow brute-force login attempts.
# SRS Traceability: Supports SRS v5.0 SE-008.
# SDD Traceability: Supports SDD v5.0 API security.
# =============================================================================

from __future__ import annotations  # Enables modern type annotation behavior.

from slowapi import Limiter  # Imports the SlowAPI limiter class.
from slowapi.util import get_remote_address  # Imports the default client IP key function.

limiter = Limiter(key_func=get_remote_address)  # Creates one shared rate limiter for the FastAPI app.