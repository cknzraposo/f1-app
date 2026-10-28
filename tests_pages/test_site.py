"""Optional site tests, independent of the application's pytest dependencies."""

import os
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown import Markdown
from mkdocs.config import load_config

from scripts.pages_links import DOCS, ROOT, SourceLinksExtension, heading_slug, rewrite_target


REPOSITORY = "https://github.com/cknzraposo/f1-app"


class PageLinks(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if identifier := attributes.get("id"):
            self.ids.add(identifier)
        key = "href" if tag in {"a", "link"} else "src"
        if target := attributes.get(key):
            self.links.append(target)


class SourceLinkTests(unittest.TestCase):
    def test_numbered_headings_have_selector_safe_anchors(self):
        self.assertEqual(heading_slug("1. Explore, do not edit", "-"), "step-1-explore-do-not-edit")
        self.assertEqual(heading_slug("Capability and access check", "-"), "capability-and-access-check")

    def test_guides_remain_local(self):
        self.assertEqual(
            rewrite_target("./setup.md#capability-and-access-check", DOCS / "index.md", REPOSITORY, "abc123"),
            "./setup.md#capability-and-access-check",
        )

    def test_readme_links_use_landing_page(self):
        self.assertEqual(
            rewrite_target("./README.md", DOCS / "setup.md", REPOSITORY, "abc123"),
            "index.md",
        )

    def test_source_links_preserve_revision_and_fragment(self):
        self.assertEqual(
            rewrite_target("../../app/query_parser.py#L1", DOCS / "repair-lab.md", REPOSITORY, "abc123"),
            f"{REPOSITORY}/blob/abc123/app/query_parser.py#L1",
        )

    def test_directories_use_github_tree(self):
        self.assertEqual(
            rewrite_target("../../.github/agents", DOCS / "copilot-spec-kit.md", REPOSITORY, "abc123"),
            f"{REPOSITORY}/tree/abc123/.github/agents",
        )

    def test_checks_are_source_links_not_published_files(self):
        self.assertEqual(
            rewrite_target("./checks/repair_checks.py", DOCS / "repair-lab.md", REPOSITORY, "abc123"),
            f"{REPOSITORY}/blob/abc123/_docs/tutorials/checks/repair_checks.py",
        )

    def test_missing_source_link_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, "missing link target"):
            rewrite_target("../../missing-file.py", DOCS / "setup.md", REPOSITORY, "abc123")

    def test_external_links_are_unchanged(self):
        for target in ["https://example.com/a", "//example.com/a", "#heading", "mailto:tutor@example.com"]:
            with self.subTest(target=target):
                self.assertEqual(
                    rewrite_target(target, DOCS / "index.md", REPOSITORY, "abc123"), target
                )

    def test_markdown_extension_leaves_code_examples_literal(self):
        renderer = Markdown(
            extensions=[
                "fenced_code",
                SourceLinksExtension(
                    source=str(DOCS / "setup.md"),
                    repository_url=REPOSITORY,
                    ref="abc123",
                ),
            ]
        )
        rendered = renderer.convert(
            "`[example](../../missing.py)`\n\n"
            "```\n[example](../../also-missing.py)\n```\n\n"
            "[actual](../../app/query_parser.py)"
        )
        self.assertIn("[example](../../missing.py)", rendered)
        self.assertIn("[example](../../also-missing.py)", rendered)
        self.assertIn(f'href="{REPOSITORY}/blob/abc123/app/query_parser.py"', rendered)


class BuiltSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="f1-pages-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.site = Path(cls.temporary.name)
        config = load_config(config_file=str(ROOT / "mkdocs.yml"))
        if not config.site_url:
            raise ValueError("The published site requires site_url")
        cls.base_path = urlsplit(config.site_url).path
        environment = dict(os.environ, PAGES_SOURCE_REF="site-test-ref")
        subprocess.run(
            [
                sys.executable, "-m", "mkdocs", "build", "--strict",
                "--site-dir", str(cls.site),
            ],
            cwd=ROOT,
            env=environment,
            check=True,
        )
        cls.pages = {
            path: PageLinks(path.read_text(encoding="utf-8"))
            for path in cls.site.rglob("*.html")
        }

    def test_landing_and_all_lessons_exist(self):
        for name in [
            "index", "setup", "copilot-native", "copilot-spec-kit",
            "repair-lab", "feature-lab", "assessment", "publishing",
        ]:
            with self.subTest(page=name):
                self.assertIn(self.site / f"{name}.html", self.pages)

    def test_in_page_navigation_anchors_are_selector_safe(self):
        for page, parsed in self.pages.items():
            for link in parsed.links:
                target = urlsplit(link)
                if not target.path and target.fragment:
                    with self.subTest(page=page.name, link=link):
                        self.assertFalse(unquote(target.fragment)[:1].isdigit())

    def test_all_local_links_assets_and_fragments_resolve(self):
        for page, parsed in self.pages.items():
            for link in parsed.links:
                target = urlsplit(link)
                if target.scheme or target.netloc:
                    continue
                with self.subTest(page=page.name, link=link):
                    if target.path.startswith("/"):
                        self.assertEqual(page.name, "404.html")
                        self.assertTrue(target.path.startswith(self.base_path))
                        destination = self.site / unquote(target.path.removeprefix(self.base_path))
                    else:
                        destination = (page.parent / unquote(target.path)).resolve() if target.path else page
                    if destination.is_dir():
                        destination /= "index.html"
                    self.assertTrue(destination.is_relative_to(self.site))
                    self.assertTrue(destination.is_file(), f"Missing generated target: {link}")
                    if target.fragment and destination in self.pages:
                        self.assertIn(unquote(target.fragment), self.pages[destination].ids)

    def test_only_documentation_is_published(self):
        for name in ["app", "f1data", "config.json", ".env", "checks", "README.html"]:
            self.assertFalse((self.site / name).exists(), name)
        self.assertFalse(list(self.site.rglob("*.py")))

    def test_source_links_use_build_revision(self):
        repair = (self.site / "repair-lab.html").read_text(encoding="utf-8")
        self.assertIn("/blob/site-test-ref/app/query_parser.py", repair)

    def test_landing_has_both_paths_and_hosting_boundary(self):
        home = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="copilot-native.html"', home)
        self.assertIn('href="copilot-spec-kit.html"', home)
        self.assertIn("run FastAPI locally", home)
        self.assertTrue((self.site / "search" / "search_index.json").is_file())


if __name__ == "__main__":
    unittest.main()
