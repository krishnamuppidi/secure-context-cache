from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://krishnamuppidi.github.io/secure-context-cache/"
SEO_PAGES = {
    "index.html": BASE_URL,
    "llm-token-optimization/index.html": f"{BASE_URL}llm-token-optimization/",
    "secure-context-caching/index.html": f"{BASE_URL}secure-context-caching/",
    "least-privilege-ai-context/index.html": f"{BASE_URL}least-privilege-ai-context/",
    "ai-agent-context-gateway/index.html": f"{BASE_URL}ai-agent-context-gateway/",
    "iac-ai-security-review/index.html": f"{BASE_URL}iac-ai-security-review/",
}


class PageMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.links: dict[str, str] = {}
        self.scripts: list[str] = []
        self.json_ld: list[str] = []
        self._json_ld_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta[key] = attributes.get("content", "")
        if tag == "link" and attributes.get("rel"):
            self.links[attributes["rel"]] = attributes.get("href", "")
        if tag == "script":
            source = attributes.get("src")
            if source:
                self.scripts.append(source)
            if attributes.get("type") == "application/ld+json":
                self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._json_ld_parts is not None:
            self.json_ld.append("".join(self._json_ld_parts))
            self._json_ld_parts = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)


def parse_page(path: Path) -> PageMetadataParser:
    parser = PageMetadataParser()
    parser.feed(path.read_text())
    return parser


def test_every_public_page_has_unique_crawlable_metadata() -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()

    for relative_path, canonical in SEO_PAGES.items():
        path = SITE / relative_path
        assert path.is_file()
        parser = parse_page(path)

        assert parser.title
        assert parser.title not in titles
        titles.add(parser.title)

        description = parser.meta.get("description", "")
        assert 80 <= len(description) <= 180
        assert description not in descriptions
        descriptions.add(description)

        assert parser.meta["robots"] == "index, follow, max-image-preview:large"
        assert parser.links["canonical"] == canonical
        assert parser.meta["og:url"] == canonical
        assert parser.meta["og:title"]
        assert parser.meta["og:description"]
        assert parser.meta["twitter:card"] == "summary"
        assert len(parser.json_ld) == 1
        structured_data = json.loads(parser.json_ld[0])
        assert structured_data["@context"] == "https://schema.org"


def test_all_pages_preserve_consent_gated_analytics_controls() -> None:
    for relative_path in SEO_PAGES:
        html = (SITE / relative_path).read_text()
        parser = parse_page(SITE / relative_path)

        expected_script = "analytics.js" if relative_path == "index.html" else "../analytics.js"
        assert expected_script in parser.scripts
        assert 'id="analytics-consent"' in html
        assert 'id="analytics-preferences"' in html
        assert 'data-analytics-choice="granted"' in html
        assert 'data-analytics-choice="denied"' in html


def test_sitemap_matches_public_pages_and_robots_advertises_it() -> None:
    sitemap_path = SITE / "sitemap.xml"
    root = ET.parse(sitemap_path).getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {item.text for item in root.findall("s:url/s:loc", namespace)}
    text_sitemap_urls = {
        line.strip()
        for line in (SITE / "sitemap.txt").read_text().splitlines()
        if line.strip()
    }

    assert sitemap_urls == set(SEO_PAGES.values())
    assert text_sitemap_urls == set(SEO_PAGES.values())
    assert all(url.startswith(BASE_URL) for url in sitemap_urls)

    robots = (SITE / "robots.txt").read_text()
    assert "User-agent: *" in robots
    assert "Allow: /" in robots
    assert f"Sitemap: {BASE_URL}sitemap.xml" in robots
    assert f"Sitemap: {BASE_URL}sitemap.txt" in robots


def test_homepage_links_to_every_topic_page() -> None:
    homepage = (SITE / "index.html").read_text()
    for relative_path in SEO_PAGES:
        if relative_path == "index.html":
            continue
        topic = relative_path.removesuffix("index.html")
        assert f'href="{topic}"' in homepage
