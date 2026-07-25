from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://krishnamuppidi.github.io/secure-context-cache/"
AI_CRAWLERS = {
    "OAI-SearchBot",
    "ChatGPT-User",
    "Claude-SearchBot",
    "Claude-User",
    "PerplexityBot",
}


def public_pages() -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(SITE.rglob("index.html")):
        relative = path.relative_to(SITE).as_posix()
        route = relative.removesuffix("index.html")
        pages[relative] = urljoin(BASE_URL, route)
    return pages


class PageMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._hidden_depth = 0
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.json_ld: list[str] = []
        self.visible_text: list[str] = []
        self._json_ld_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._hidden_depth += 1
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta[key] = attributes.get("content", "")
        if tag == "link":
            self.links.append(attributes)
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
        if tag in {"script", "style"}:
            self._hidden_depth = max(0, self._hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
        elif not self._hidden_depth and data.strip():
            self.visible_text.append(data.strip())

    def link(self, rel: str, type_: str = "") -> str:
        for attributes in self.links:
            relations = attributes.get("rel", "").split()
            if rel in relations and (not type_ or attributes.get("type") == type_):
                return attributes.get("href", "")
        return ""


def parse_page(path: Path) -> PageMetadataParser:
    parser = PageMetadataParser()
    parser.feed(path.read_text())
    return parser


def test_every_public_page_has_unique_crawlable_metadata() -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()

    for relative_path, canonical in public_pages().items():
        path = SITE / relative_path
        parser = parse_page(path)

        assert parser.title and parser.title not in titles
        titles.add(parser.title)

        description = parser.meta.get("description", "")
        assert 80 <= len(description) <= 180, relative_path
        assert description not in descriptions
        descriptions.add(description)

        assert parser.meta["robots"] == "index, follow, max-image-preview:large"
        assert parser.link("canonical") == canonical
        assert parser.meta["og:url"] == canonical
        assert parser.meta["og:title"]
        assert parser.meta["og:description"]
        assert parser.meta["og:image"] == f"{BASE_URL}assets/secure-context-cache-social-preview.png"
        assert parser.meta["twitter:card"] == "summary_large_image"
        assert parser.meta["twitter:image"]
        assert len(parser.json_ld) == 1
        structured_data = json.loads(parser.json_ld[0])
        assert structured_data["@context"] == "https://schema.org"


def test_every_public_page_has_substantial_visible_content_and_markdown() -> None:
    for relative_path in public_pages():
        path = SITE / relative_path
        parser = parse_page(path)
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", " ".join(parser.visible_text))
        assert len(words) >= 250, (relative_path, len(words))

        markdown = path.with_name("index.md")
        assert markdown.is_file(), relative_path
        markdown_text = markdown.read_text()
        assert markdown_text.startswith("# ")
        assert "Canonical URL:" in markdown_text
        assert "GitHub" in markdown_text or "Source code:" in markdown_text
        assert parser.link("alternate", "text/markdown") == "index.md" or parser.link(
            "alternate", "text/markdown"
        ).endswith("/index.md")


def test_all_pages_preserve_consent_gated_analytics_controls() -> None:
    for relative_path in public_pages():
        html = (SITE / relative_path).read_text()
        parser = parse_page(SITE / relative_path)
        depth = len(Path(relative_path).parts) - 1
        expected_script = f"{'../' * depth}analytics.js"

        assert expected_script in parser.scripts
        assert 'id="analytics-consent"' in html
        assert 'id="analytics-preferences"' in html
        assert 'data-analytics-choice="granted"' in html
        assert 'data-analytics-choice="denied"' in html


def test_sitemap_matches_public_pages_and_robots_advertises_it() -> None:
    root = ET.parse(SITE / "sitemap.xml").getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {item.text for item in root.findall("s:url/s:loc", namespace)}
    text_sitemap_urls = {
        line.strip() for line in (SITE / "sitemap.txt").read_text().splitlines() if line.strip()
    }
    expected_urls = set(public_pages().values())

    assert sitemap_urls == expected_urls
    assert text_sitemap_urls == expected_urls
    assert all(url.startswith(BASE_URL) for url in sitemap_urls)

    robots = (SITE / "robots.txt").read_text()
    assert "User-agent: *\nAllow: /" in robots
    for crawler in AI_CRAWLERS:
        assert f"User-agent: {crawler}\nAllow: /" in robots
    assert f"Sitemap: {BASE_URL}sitemap.xml" in robots
    assert f"Sitemap: {BASE_URL}sitemap.txt" in robots


def test_machine_readable_discovery_files_cover_every_page() -> None:
    llms = (SITE / "llms.txt").read_text()
    llms_full = (SITE / "llms-full.txt").read_text()
    assert "Claim boundary:" in llms
    assert "32-to-16" in llms
    assert "75.3%" in llms
    assert "not independent adoption evidence" in llms

    for url in public_pages().values():
        assert url in llms or url in llms_full

    feed = ET.parse(SITE / "feed.xml").getroot()
    assert feed.tag == "rss"
    assert feed.find("channel/title").text == "Secure Context Cache Updates"


def test_indexnow_payload_matches_sitemap_and_key_file() -> None:
    payload = json.loads((SITE / "indexnow-urls.json").read_text())
    sitemap_urls = [
        line.strip() for line in (SITE / "sitemap.txt").read_text().splitlines() if line.strip()
    ]
    key = payload["key"]

    assert payload["host"] == "krishnamuppidi.github.io"
    assert payload["keyLocation"] == f"{BASE_URL}{key}.txt"
    assert payload["urlList"] == sitemap_urls
    assert (SITE / f"{key}.txt").read_text().strip() == key


def test_homepage_and_docs_link_to_priority_resources() -> None:
    homepage = (SITE / "index.html").read_text()
    docs = (SITE / "docs/index.html").read_text()
    for route in (
        "docs/",
        "secure-context-cache-benchmark/",
        "prompt-caching-vs-context-caching/",
        "mcp-context-optimization/",
    ):
        assert f'href="{route}"' in homepage
    assert "API Reference" in docs
    assert "Production Readiness" in docs
