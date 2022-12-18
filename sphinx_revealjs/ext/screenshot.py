"""Extension to generate screenshot for first page of presentation.

This is optional extension.
You need install extra and configure to use it.
"""
from pathlib import Path
from typing import Any, Dict, Set

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError
from sphinx.util.docutils import nodes
from sphinx.util.logging import getLogger
from sphinx.util.matching import Matcher

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    msg = (
        f"{__name__} need playwright."
        "you should run \"pip install 'sphinx-revealjs[screenshot]'\"."
    )
    raise ExtensionError(msg)

from .. import __version__ as core_version

logger = getLogger(__name__)
_targets: Dict[str, str] = dict()


def collect_screenshot_targets(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
):
    global _targets
    _targets = {}
    for docname in added:
        _targets[docname] = f"{app.config.revealjs_screenshot_outdir}/{docname}.png"
    for docname in changed:
        _targets[docname] = f"{app.config.revealjs_screenshot_outdir}/{docname}.png"
    return []


def insert_og_image(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: nodes.document,
):
    image_url = f"{app.config.revealjs_screenshot_urlbase}/{_targets[pagename]}"
    context.setdefault("metatags", "")
    context["metatags"] += f'\n<meta property="og:image" content="{image_url}" >'


def generate_screenshots(app: Sphinx, exception: Exception):
    logger.info("Generating screenshot")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        matcher = Matcher(app.config.revealjs_screenshot_excludes)
        for docname, image_url in _targets.items():
            if matcher(docname):
                continue
            page_path = Path(app.outdir) / app.builder.get_target_uri(docname)
            if page_path.is_dir():
                page_path = page_path / "index.html"
            image_path = Path(app.outdir) / image_url
            page.goto(f"file://{page_path}")
            conf = page.evaluate("Reveal.getConfig()")
            page.set_viewport_size({"width": conf["width"], "height": conf["height"]})
            page.screenshot(path=image_path)


def setup(app: Sphinx):
    """Entryoint."""
    app.add_config_value("revealjs_screenshot_urlbase", "http://localhost:8000", "env")
    app.add_config_value("revealjs_screenshot_outdir", "_images/ogp", "env")
    app.add_config_value("revealjs_screenshot_excludes", [], "env")
    app.connect("env-get-outdated", collect_screenshot_targets)
    app.connect("html-page-context", insert_og_image)
    app.connect("build-finished", generate_screenshots)
    return {
        "version": core_version,
        "env_version": 1,
        "parallel_read_safe": True,
    }
