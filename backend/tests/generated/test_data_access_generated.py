# =============================================================================
# File: test_data_access_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate ObjectId validation cases for the Data Access Layer.
# Security Note: Tests generate fake strings only and do not connect to MongoDB.
# SRS Traceability: Supports SRS v5.0 SE-009 and backend testing requirements.
# SDD Traceability: Supports SDD v5.0 typed validation and Data Access Layer design.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

import pytest  # Imports pytest for exception assertions.
from bson import ObjectId  # Imports ObjectId for MongoDB ID validation.
from hypothesis import given  # Imports the Hypothesis generated-test decorator.
from hypothesis import (
    settings,
)  # Imports Hypothesis settings for controlling generated cases.
from hypothesis import (
    strategies as st,
)  # Imports Hypothesis strategies for generated inputs.

from backend.data_access.base import (
    normalize_object_id,
)  # Imports the ObjectId normalization helper.


@given(
    st.text().filter(lambda value: not ObjectId.is_valid(value))
)  # Generates invalid ObjectId strings.
@settings(max_examples=200)  # Runs this generated test with 200 examples.
def test_generated_invalid_object_ids_are_rejected(
    value: str,
) -> None:  # Tests generated invalid IDs.
    with pytest.raises(ValueError):  # Expects invalid IDs to raise ValueError.
        normalize_object_id(value)  # Attempts to normalize the generated invalid ID.


@given(st.just(str(ObjectId())))  # Generates a valid ObjectId string.
def test_generated_valid_object_ids_are_accepted(
    value: str,
) -> None:  # Tests generated valid IDs.
    result = normalize_object_id(value)  # Normalizes the valid ObjectId string.
    assert isinstance(result, ObjectId)  # Verifies the result is an ObjectId.
