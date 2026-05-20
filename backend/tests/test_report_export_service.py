# =============================================================================
# File: backend/tests/test_report_export_service.py
# Project: Grocery Intelligence Platform
# Description: Tests P1-19C report export service.
# =============================================================================

from __future__ import annotations  # Enables modern Python type-hint behavior.

import sys  # Supports monkeypatching imported modules.

from backend.services.report_export_service import ReportExportService  # Imports export service under test.


def sample_report() -> dict:  # Builds reusable report fixture.
    return {  # Starts report payload.
        "week_of": "2026-05-04",  # Sets report week.
        "generated_at": "2026-05-20T00:00:00+00:00",  # Sets generated timestamp.
        "summary": {  # Starts summary.
            "total_oop": 10.00,  # Sets OOP.
            "total_register_savings": 2.00,  # Sets register savings.
            "total_rewards_value": 3.00,  # Sets rewards.
            "total_rebates_back": 1.00,  # Sets rebates.
            "final_after_rewards": 6.00,  # Sets display-only final.
            "money_maker_count": 1,  # Sets money-maker count.
        },  # Ends summary.
        "stores": [  # Starts stores.
            {  # Starts store.
                "store_ref": "heb-001",  # Sets store ref.
                "totals": {  # Starts store totals.
                    "total_oop": 10.00,  # Sets store OOP.
                    "total_rewards_value": 3.00,  # Sets store rewards.
                    "total_rebates_back": 1.00,  # Sets store rebates.
                    "final_after_rewards": 6.00,  # Sets store final.
                },  # Ends store totals.
                "deals": [  # Starts deals.
                    {  # Starts deal.
                        "product_ref": "product-001",  # Sets product ref.
                        "register_price": 10.00,  # Sets register price.
                        "out_of_pocket": 10.00,  # Sets OOP.
                        "coupon_refs": ["heb-coupon-001"],  # Sets coupon refs.
                        "reward_offers": [  # Starts reward offers.
                            {  # Starts first reward offer.
                                "reward_provider": "Ibotta",  # Sets reward provider.
                                "receipt_required": True,  # Marks receipt-required reward.
                                "claim_required": False,  # Marks no claim requirement.
                            },  # Ends first reward offer.
                            {  # Starts second reward offer.
                                "reward_provider": "Aisle",  # Sets reward provider.
                                "receipt_required": False,  # Marks no receipt requirement.
                                "claim_required": True,  # Marks claim-required reward.
                            },  # Ends second reward offer.
                        ],  # Ends reward offers.
                        "total_rebates_back": 1.00,  # Sets rebates.
                        "final_after_rewards": 6.00,  # Sets display-only final.
                        "is_money_maker": True,  # Marks money maker.
                    },  # Ends deal.
                ],  # Ends deals.
            },  # Ends store.
        ],  # Ends stores.
    }  # Ends report payload.


def test_build_docx_returns_docx_bytes() -> None:  # Verifies DOCX generation.
    service = ReportExportService()  # Creates export service.
    docx_bytes = service.build_docx(report=sample_report())  # Builds DOCX bytes.
    assert isinstance(docx_bytes, bytes)  # Confirms bytes output.
    assert docx_bytes.startswith(b"PK")  # Confirms DOCX zip signature.


def test_pdf_html_keeps_coupons_and_rewards_separate() -> None:  # Verifies financial separation text.
    service = ReportExportService()  # Creates export service.
    html = service._build_html(report=sample_report())  # Builds HTML for inspection.
    assert "H-E-B coupons" in html  # Confirms coupons label exists.
    assert "Reward offers" in html  # Confirms rewards label exists.
    assert "Receipt-required rewards" in html  # Confirms receipt-required label exists.
    assert "Claim-required rewards" in html  # Confirms claim-required label exists.
    assert "Final after rewards is informational" in html  # Confirms final value note exists.


def test_build_pdf_returns_pdf_bytes(monkeypatch) -> None:  # Verifies PDF generation without native WeasyPrint.
    class FakeHTML:  # Defines fake WeasyPrint HTML class.
        def __init__(self, string: str) -> None:  # Accepts HTML string input.
            self.string = string  # Stores HTML string for inspection.

        def write_pdf(self) -> bytes:  # Simulates PDF generation.
            return b"%PDF-FAKE"  # Returns fake PDF bytes.

    fake_weasyprint = type("FakeWeasyPrint", (), {"HTML": FakeHTML})  # Creates fake WeasyPrint module object.
    monkeypatch.setitem(sys.modules, "weasyprint", fake_weasyprint)  # Replaces WeasyPrint import for test.

    service = ReportExportService()  # Creates export service.
    pdf_bytes = service.build_pdf(report=sample_report())  # Builds PDF bytes.
    assert pdf_bytes.startswith(b"%PDF")  # Confirms PDF-like signature.


def test_empty_report_still_exports(monkeypatch) -> None:  # Verifies empty report export.
    class FakeHTML:  # Defines fake WeasyPrint HTML class.
        def __init__(self, string: str) -> None:  # Accepts HTML string input.
            self.string = string  # Stores HTML string for inspection.

        def write_pdf(self) -> bytes:  # Simulates PDF generation.
            return b"%PDF-FAKE"  # Returns fake PDF bytes.

    fake_weasyprint = type("FakeWeasyPrint", (), {"HTML": FakeHTML})  # Creates fake WeasyPrint module object.
    monkeypatch.setitem(sys.modules, "weasyprint", fake_weasyprint)  # Replaces WeasyPrint import for test.

    service = ReportExportService()  # Creates export service.
    report = {"week_of": "2026-05-04", "generated_at": "now", "summary": {}, "stores": []}  # Creates empty report.
    assert service.build_pdf(report=report).startswith(b"%PDF")  # Confirms PDF-like output.
    assert service.build_docx(report=report).startswith(b"PK")  # Confirms DOCX output.