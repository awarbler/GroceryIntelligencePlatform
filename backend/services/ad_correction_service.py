# =============================================================================
# File: backend/services/ad_correction_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Store short-lived H-E-B weekly ad correction sessions.
# Security Note: Stores public ad data only and no credentials.
# SRS Traceability: Supports SRS v5.0 Section 13 human correction workflow.
# SDD Traceability: Supports SDD v5.0 correction-session design.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

from backend.models.ad_correction import AdCorrectionSession  # Imports ad correction session model.


class AdCorrectionSessionNotFoundError(LookupError):  # Defines missing session error.
    """Raised when an ad correction session cannot be found."""  # Documents error purpose.


class AdCorrectionSessionStore:  # Defines in-memory ad session store.
    """Stores ad correction sessions for local Phase 1 development."""  # Documents store purpose.

    def __init__(self) -> None:  # Initializes store.
        self._sessions: dict[str, AdCorrectionSession] = {}  # Stores sessions by ID.

    def create_session(self, session: AdCorrectionSession) -> AdCorrectionSession:  # Saves new session.
        self._sessions[session.session_id] = session  # Stores session by ID.
        return session  # Returns saved session.

    def get_session(self, session_id: str) -> AdCorrectionSession:  # Reads session.
        session: AdCorrectionSession | None = self._sessions.get(session_id)  # Looks up session.
        if session is None:  # Handles missing session.
            raise AdCorrectionSessionNotFoundError(session_id)  # Raises not-found error.
        return session  # Returns found session.

    def delete_session(self, session_id: str) -> None:  # Removes session after approval.
        self._sessions.pop(session_id, None)  # Deletes session if present.

    def clear(self) -> None:  # Clears sessions for tests.
        self._sessions.clear()  # Removes all sessions.


ad_correction_session_store: AdCorrectionSessionStore = AdCorrectionSessionStore()  # Creates shared store.