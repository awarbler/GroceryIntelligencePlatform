# =============================================================================  # File header separator.
# File: correction_service.py  # Identifies this service file.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Author: Anita Woodford  # Identifies the project author.
# Description: Provides in-memory correction-session storage with 24-hour TTL for P1-11.  # Explains the file purpose.
# Security Note: This service stores temporary parsed grocery data only and must not store secrets.  # States security boundary.
# SRS Traceability: Supports SRS v5.0 Section 13 HC-001 through HC-009.  # Maps to SRS.
# SDD Traceability: Supports SDD v5.0 correction-session workflow and API endpoint design.  # Maps to SDD.
# =============================================================================  # File header separator.

from __future__ import annotations  # Enables modern type hint behavior.

from datetime import UTC  # Imports UTC for timezone-aware timestamps.
from datetime import datetime  # Imports datetime for expiration checks.
from datetime import timedelta  # Imports timedelta for 24-hour TTL.
from uuid import uuid4  # Imports uuid4 for unique session IDs.

from backend.models.correction import AUTO_ACCEPT_THRESHOLD  # Imports the auto-accept threshold.
from backend.models.correction import REVIEW_REQUIRED_THRESHOLD  # Imports the required-review threshold.
from backend.models.correction import CorrectionItem  # Imports the correction item model.
from backend.models.correction import CorrectionItemUpdateRequest  # Imports the item update request model.
from backend.models.correction import CorrectionSession  # Imports the correction session model.


SESSION_TTL_HOURS: int = 24  # Defines the P1-11 correction-session TTL.


class CorrectionSessionNotFoundError(KeyError):  # Defines an error for missing or expired sessions.
    """Raised when a correction session does not exist or has expired."""  # Documents the error purpose.


class CorrectionItemNotFoundError(KeyError):  # Defines an error for missing correction items.
    """Raised when a correction item does not exist in a session."""  # Documents the error purpose.


class InMemoryCorrectionSessionStore:  # Defines the development fallback session store.
    """Stores correction sessions in memory with a 24-hour TTL."""  # Documents the store behavior.

    def __init__(self) -> None:  # Initializes the in-memory store.
        self._sessions: dict[str, CorrectionSession] = {}  # Stores sessions by session_id.

    def create_session(  # Defines session creation behavior.
        self,  # Receives the store instance.
        source_type: str,  # Receives the source type.
        store: str,  # Receives the store label.
        raw_lines: list[str],  # Receives raw receipt lines.
        items: list[CorrectionItem],  # Receives parsed and normalized correction items.
        parse_errors: list[str],  # Receives parser errors.
        source_metadata: dict[str, object],  # Receives source metadata.
    ) -> CorrectionSession:  # Returns the created correction session.
        now: datetime = datetime.now(UTC)  # Captures the current UTC timestamp.
        session_id: str = str(uuid4())  # Creates a unique session ID.
        session: CorrectionSession = CorrectionSession(  # Builds a correction session model.
            session_id=session_id,  # Stores the session ID.
            source_type=source_type,  # Stores the source type.
            store=store,  # Stores the store label.
            raw_lines=raw_lines,  # Stores raw receipt lines.
            items=[apply_confidence_flags(item) for item in items],  # Stores items with confidence flags.
            parse_errors=parse_errors,  # Stores parser errors.
            source_metadata=source_metadata,  # Stores source metadata.
            created_at=now,  # Stores creation time.
            expires_at=now + timedelta(hours=SESSION_TTL_HOURS),  # Stores expiration time.
            approved=False,  # Starts the session as not approved.
        )  # Ends session model creation.
        self._sessions[session_id] = session  # Saves the session in memory.
        return session  # Returns the created session.

    def get_session(self, session_id: str) -> CorrectionSession:  # Retrieves a session by ID.
        self._purge_expired_sessions()  # Removes expired sessions before lookup.
        session: CorrectionSession | None = self._sessions.get(session_id)  # Reads the session from memory.
        if session is None:  # Checks whether the session is missing.
            raise CorrectionSessionNotFoundError(session_id)  # Raises a not-found error.
        return session  # Returns the active session.

    def update_item(  # Defines item update behavior.
        self,  # Receives the store instance.
        session_id: str,  # Receives the session ID.
        item_id: str,  # Receives the item ID.
        update_request: CorrectionItemUpdateRequest,  # Receives validated update fields.
    ) -> CorrectionSession:  # Returns the updated correction session.
        session: CorrectionSession = self.get_session(session_id)  # Retrieves the active session.
        updated_items: list[CorrectionItem] = []  # Creates a list for updated items.
        found: bool = False  # Tracks whether the target item was found.

        for item in session.items:  # Iterates through existing items.
            if item.item_id != item_id:  # Checks whether this is not the target item.
                updated_items.append(item)  # Keeps non-target items unchanged.
                continue  # Moves to the next item.

            update_data: dict[str, object] = update_request.model_dump(exclude_unset=True)  # Keeps only supplied fields.
            update_data["user_corrected"] = True  # Marks the item as corrected by the owner.
            updated_item: CorrectionItem = item.model_copy(update=update_data)  # Creates an updated item copy.
            updated_items.append(apply_confidence_flags(updated_item))  # Reapplies confidence flags.
            found = True  # Marks the target item as found.

        if not found:  # Checks whether no item matched.
            raise CorrectionItemNotFoundError(item_id)  # Raises an item not-found error.

        updated_session: CorrectionSession = session.model_copy(update={"items": updated_items})  # Creates updated session copy.
        self._sessions[session_id] = updated_session  # Saves updated session.
        return updated_session  # Returns updated session.

    def replace_item(self, session_id: str, updated_item: CorrectionItem) -> CorrectionSession:  # Replaces one item after normalization changes.
        session: CorrectionSession = self.get_session(session_id)  # Retrieves the active session.
        updated_items: list[CorrectionItem] = []  # Creates a list for updated items.
        found: bool = False  # Tracks whether the target item was found.

        for item in session.items:  # Iterates through session items.
            if item.item_id == updated_item.item_id:  # Checks whether this is the target item.
                updated_items.append(apply_confidence_flags(updated_item))  # Adds the updated item with flags.
                found = True  # Marks the target item as found.
            else:  # Handles non-target items.
                updated_items.append(item)  # Keeps the existing item.

        if not found:  # Checks whether no item matched.
            raise CorrectionItemNotFoundError(updated_item.item_id)  # Raises an item not-found error.

        updated_session: CorrectionSession = session.model_copy(update={"items": updated_items})  # Creates updated session copy.
        self._sessions[session_id] = updated_session  # Saves updated session.
        return updated_session  # Returns updated session.

    def mark_approved(self, session_id: str) -> CorrectionSession:  # Marks a session as approved.
        session: CorrectionSession = self.get_session(session_id)  # Retrieves the active session.
        updated_session: CorrectionSession = session.model_copy(update={"approved": True})  # Marks session as approved.
        self._sessions[session_id] = updated_session  # Saves updated session.
        return updated_session  # Returns approved session.

    def expire_session_for_test(self, session_id: str) -> None:  # Supports testing expiration behavior.
        session: CorrectionSession = self.get_session(session_id)  # Retrieves the active session.
        expired_session: CorrectionSession = session.model_copy(update={"expires_at": datetime.now(UTC) - timedelta(seconds=1)})  # Forces expiration.
        self._sessions[session_id] = expired_session  # Saves expired session.

    def clear(self) -> None:  # Clears all sessions, mainly for tests.
        self._sessions.clear()  # Removes all sessions from memory.

    def _purge_expired_sessions(self) -> None:  # Removes expired sessions.
        now: datetime = datetime.now(UTC)  # Captures the current UTC timestamp.
        expired_ids: list[str] = [session_id for session_id, session in self._sessions.items() if session.expires_at <= now]  # Finds expired IDs.
        for session_id in expired_ids:  # Iterates through expired IDs.
            self._sessions.pop(session_id, None)  # Removes each expired session safely.


def apply_confidence_flags(item: CorrectionItem) -> CorrectionItem:  # Applies P1-11 confidence flags to an item.
    review_required: bool = item.confidence < REVIEW_REQUIRED_THRESHOLD  # Checks low-confidence review requirement.
    review_suggested: bool = REVIEW_REQUIRED_THRESHOLD <= item.confidence < AUTO_ACCEPT_THRESHOLD  # Checks medium-confidence review suggestion.
    auto_accepted: bool = item.confidence >= AUTO_ACCEPT_THRESHOLD  # Checks high-confidence auto-accepted state.
    return item.model_copy(  # Returns an updated item copy.
        update={  # Starts update values.
            "review_required": review_required,  # Stores required-review flag.
            "review_suggested": review_suggested,  # Stores suggested-review flag.
            "auto_accepted": auto_accepted,  # Stores auto-accepted flag.
        }  # Ends update values.
    )  # Ends model copy.


correction_session_store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates the shared in-memory session store.