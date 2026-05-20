# =============================================================================
# File: backend/tests/api/test_reports_api.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-19B report JSON API endpoint.
# SRS Traceability: SRS Section 16 DR-001 through DR-021; SRS Section 20 TS-005.
# SDD Traceability: SDD Section 8 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints.

from unittest.mock import AsyncMock, MagicMock  # Supports route dependency mocking.

from fastapi.testclient import TestClient  # Supports FastAPI endpoint testing.

from backend.api.reports import get_report_service  # Imports dependency override target.
from backend.main import app  # Imports FastAPI app.
from backend.services.report_service import ReportService  # Imports service type.


def _fake_report() -> dict:  # Builds fake report payload.
    return {  # Starts fake report.
        "week_of": "2026-05-18",  # Stores week.
        "generated_at": "2026-05-18T10:00:00Z",  # Stores timestamp.
        "summary": {  # Starts summary.
            "total_opportunities": 1,  # Stores opportunity count.
            "total_oop": 2.99,  # Stores OOP.
            "total_register_savings": 1.01,  # Stores register savings.
            "total_rewards_value": 1.00,  # Stores rewards.
            "total_rebates_back": 0.50,  # Stores rebates.
            "final_after_rewards": 1.49,  # Stores display-only final.
            "money_maker_count": 0,  # Stores money-maker count.
        },  # Ends summary.
        "stores": [  # Starts stores.
            {  # Starts store.
                "store_ref": "heb",  # Stores store ref.
                "totals": {  # Starts totals.
                    "total_opportunities": 1,  # Stores count.
                    "total_oop": 2.99,  # Stores OOP.
                    "total_rewards_value": 1.00,  # Stores rewards.
                    "total_rebates_back": 0.50,  # Stores rebates.
                    "final_after_rewards": 1.49,  # Stores final.
                    "money_maker_count": 0,  # Stores money-maker count.
                },  # Ends totals.
                "deals": [],  # Stores deal cards.
            }  # Ends store.
        ],  # Ends stores.
        "match_count": 1,  # Stores match count.
    }  # Ends fake report.


def _make_fake_service(report: dict | None = None) -> ReportService:  # Creates fake report service.
    service = MagicMock(spec=ReportService)  # Creates service mock.
    service.generate_weekly_report = AsyncMock(return_value=report or _fake_report())  # Mocks async report call.
    return service  # Returns fake service.


def _override_service(service: ReportService) -> None:  # Installs dependency override.
    app.dependency_overrides[get_report_service] = lambda: service  # Overrides report service dependency.


def _clear_overrides() -> None:  # Clears dependency overrides.
    app.dependency_overrides.clear()  # Removes all overrides.


def test_generate_report_returns_200() -> None:  # Tests successful request.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=2026-05-18")  # Calls endpoint.
    _clear_overrides()  # Clears override.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["success"] is True  # Verifies standard response.


def test_generate_report_missing_week_of_returns_422() -> None:  # Tests required week_of.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate")  # Calls endpoint without week_of.
    _clear_overrides()  # Clears override.
    assert response.status_code == 422  # Verifies validation failure.


def test_generate_report_invalid_date_returns_422() -> None:  # Tests invalid date.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=not-a-date")  # Calls endpoint with bad date.
    _clear_overrides()  # Clears override.
    assert response.status_code == 422  # Verifies validation failure.


def test_generate_report_returns_grouped_stores() -> None:  # Tests store payload.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=2026-05-18")  # Calls endpoint.
    _clear_overrides()  # Clears override.
    assert response.json()["data"]["stores"][0]["store_ref"] == "heb"  # Verifies grouped store.


def test_generate_report_summary_keeps_financial_fields_separate() -> None:  # Tests financial separation.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=2026-05-18")  # Calls endpoint.
    _clear_overrides()  # Clears override.
    summary = response.json()["data"]["summary"]  # Reads summary.
    assert "total_oop" in summary  # Verifies OOP field.
    assert "total_rewards_value" in summary  # Verifies rewards field.
    assert "total_rebates_back" in summary  # Verifies rebate field.
    assert "final_after_rewards" in summary  # Verifies display-only final.
    assert "money_maker_count" in summary  # Verifies money-maker count.


def test_generate_report_meta_contains_counts() -> None:  # Tests metadata.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=2026-05-18")  # Calls endpoint.
    _clear_overrides()  # Clears override.
    meta = response.json()["meta"]  # Reads meta.
    assert meta["week_of"] == "2026-05-18"  # Verifies week meta.
    assert meta["match_count"] == 1  # Verifies match count meta.
    assert meta["store_count"] == 1  # Verifies store count meta.


def test_generate_report_passes_store_ref_filter() -> None:  # Tests store_ref propagation.
    service = _make_fake_service()  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    client.get("/api/v1/report/generate?week_of=2026-05-18&store_ref=heb")  # Calls endpoint with filter.
    _clear_overrides()  # Clears override.
    call_kwargs = service.generate_weekly_report.call_args.kwargs  # Reads service call args.
    assert call_kwargs["store_ref"] == "heb"  # Verifies filter propagation.


def test_generate_report_empty_report_returns_empty_stores() -> None:  # Tests empty report.
    empty_report = {  # Starts empty report.
        "week_of": "2026-05-18",  # Stores week.
        "generated_at": "2026-05-18T10:00:00Z",  # Stores timestamp.
        "summary": {  # Starts summary.
            "total_opportunities": 0,  # Stores zero opportunities.
            "total_oop": 0.0,  # Stores zero OOP.
            "total_register_savings": 0.0,  # Stores zero savings.
            "total_rewards_value": 0.0,  # Stores zero rewards.
            "total_rebates_back": 0.0,  # Stores zero rebates.
            "final_after_rewards": 0.0,  # Stores zero final.
            "money_maker_count": 0,  # Stores zero money makers.
        },  # Ends summary.
        "stores": [],  # Stores empty stores.
        "match_count": 0,  # Stores zero matches.
    }  # Ends empty report.
    service = _make_fake_service(empty_report)  # Creates fake service.
    _override_service(service)  # Overrides dependency.
    client = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/report/generate?week_of=2026-05-18")  # Calls endpoint.
    _clear_overrides()  # Clears override.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["data"]["stores"] == []  # Verifies empty stores.