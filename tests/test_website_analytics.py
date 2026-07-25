from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MEASUREMENT_ID = "G-9C5B48SR3B"


def test_website_loads_consent_gated_analytics() -> None:
    html = (SITE / "index.html").read_text()
    analytics = (SITE / "analytics.js").read_text()

    assert '<script defer src="analytics.js"></script>' in html
    assert f'const MEASUREMENT_ID = "{MEASUREMENT_ID}"' in analytics
    assert "googletagmanager.com/gtag/js" in analytics
    assert 'storedChoice() !== "granted"' in analytics
    assert 'ad_storage: "denied"' in analytics
    assert "allow_google_signals: false" in analytics
    assert 'page_location: `${window.location.origin}${window.location.pathname}`' in analytics


def test_analytics_notice_and_preferences_are_accessible() -> None:
    html = (SITE / "index.html").read_text()

    assert 'role="dialog"' in html
    assert 'aria-labelledby="analytics-consent-title"' in html
    assert 'id="analytics-preferences"' in html
    assert 'data-analytics-choice="granted"' in html
    assert 'data-analytics-choice="denied"' in html
    assert "No names, email addresses, form contents, or full link URLs are sent." in html


def test_engagement_events_avoid_full_urls_and_personal_data() -> None:
    app = (SITE / "app.js").read_text()

    for event_name in (
        "pilot_request_click",
        "github_resource_click",
        "token_savings_cta_click",
        "token_calculator_use",
        "developer_example_tab",
        "code_example_copy",
    ):
        assert event_name in app

    assert "link.href" not in app
    assert "link.search" not in app
    assert "nagamuppidi1015@gmail.com" not in app
