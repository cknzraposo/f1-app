"""Keep tutorial Markdown useful both in the repository and on GitHub Pages."""

import os
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.etree.ElementTree import Element

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.toc import slugify
from markdown.treeprocessors import Treeprocessor
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "_docs" / "tutorials"
EXTENSION = "scripts.pages_links"


def heading_slug(value: str, separator: str) -> str:
    """Keep numbered lesson anchors valid for the theme's CSS selectors."""
    slug = slugify(value, separator)
    return f"step-{slug}" if slug[:1].isdigit() else slug


def rewrite_target(url: str, source: Path, repository_url: str, ref: str) -> str:
    """Leave guide links local and send repository-only resources to GitHub."""
    target = urlsplit(url)
    if target.scheme or target.netloc or not target.path:
        return url

    destination = (source.parent / unquote(target.path)).resolve()
    relative = destination.relative_to(ROOT)
    if not destination.exists():
        raise ValueError(f"{source.name}: missing link target {target.path}")

    if destination == DOCS / "README.md":
        path = "index.md"
    elif destination.is_relative_to(DOCS) and not destination.is_relative_to(DOCS / "checks"):
        return url
    else:
        kind = "tree" if destination.is_dir() else "blob"
        path = (
            f"{repository_url.rstrip('/')}/{kind}/{quote(ref, safe='')}/"
            f"{quote(relative.as_posix(), safe='/')}"
        )
    return urlunsplit(("", "", path, target.query, target.fragment))


class SourceLinksExtension(Extension):
    def __init__(self, **kwargs: str):
        self.config = {
            "source": ["", "Absolute Markdown source path"],
            "repository_url": ["", "GitHub repository URL"],
            "ref": ["master", "Source revision"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        processor = SourceLinksProcessor(md)
        processor.source = Path(self.getConfig("source"))
        processor.repository_url = self.getConfig("repository_url")
        processor.ref = self.getConfig("ref")
        # Inline links exist after priority 20; MkDocs resolves local URLs at 0.
        md.treeprocessors.register(processor, "tutorial_source_links", 1)


class SourceLinksProcessor(Treeprocessor):
    source: Path
    repository_url: str
    ref: str

    def run(self, root: Element) -> None:
        for element in root.iter("a"):
            href = element.get("href")
            if href is not None:
                element.set(
                    "href", rewrite_target(href, self.source, self.repository_url, self.ref)
                )


def makeExtension(**kwargs: str) -> SourceLinksExtension:
    return SourceLinksExtension(**kwargs)


def on_config(config: MkDocsConfig) -> MkDocsConfig:
    config.markdown_extensions.append(EXTENSION)
    config.mdx_configs.setdefault("toc", {})["slugify"] = heading_slug
    repository = os.environ.get("PAGES_REPOSITORY")
    if repository:
        config.repo_url = f"https://github.com/{repository}"
    branch = os.environ.get("PAGES_EDIT_BRANCH")
    if branch:
        config.edit_uri = f"edit/{quote(branch, safe='')}/_docs/tutorials/"
    return config


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str:
    if page.file.abs_src_path is None:
        raise ValueError(f"Tutorial page has no source path: {page.file.src_uri}")
    if not config.repo_url:
        raise ValueError("The tutorial site requires repo_url")
    config.mdx_configs[EXTENSION] = {
        "source": page.file.abs_src_path,
        "repository_url": config.repo_url,
        "ref": os.environ.get("PAGES_SOURCE_REF", "master"),
    }
    return markdown
