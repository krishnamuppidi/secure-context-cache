from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_relative_markdown_links_resolve() -> None:
    markdown_files = [ROOT / "README.md", ROOT / "SECURITY.md", ROOT / "CHANGELOG.md"]
    markdown_files.extend((ROOT / "docs").glob("*.md"))
    markdown_files.extend([ROOT / "deploy/aws/README.md", ROOT / "examples/clients/README.md"])

    missing: list[tuple[str, str]] = []
    for source in markdown_files:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", source.read_text()):
            path = target.strip().split("#", 1)[0]
            if not path or "://" in path or path.startswith(("mailto:", "#")):
                continue
            if not (source.parent / path).resolve().exists():
                missing.append((str(source.relative_to(ROOT)), path))

    assert not missing


def test_readme_indexes_every_documentation_guide() -> None:
    readme = (ROOT / "README.md").read_text()
    for guide in (ROOT / "docs").glob("*.md"):
        assert f"docs/{guide.name}" in readme
