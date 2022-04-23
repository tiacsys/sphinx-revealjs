"""Internal extension for Speaker view or Reveal.js."""
from docutils import nodes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from sphinx.application import Sphinx
from sphinx.directives import SphinxDirective
from sphinx.util.docutils import SphinxTranslator

from .. import __version__
from ..builders import RevealjsHTMLBuilder


class revealjs_notes(nodes.Admonition, nodes.Element):  # noqa: D101
    pass


class RevealjsNotes(BaseAdmonition, SphinxDirective):  # noqa: D101
    has_content = True
    node_class = revealjs_notes

    def run(self):  # noqa: D102
        (node,) = super().run()
        if isinstance(node, (nodes.system_message, revealjs_notes)):
            return [node]


def visit_revealjs_notes(self: SphinxTranslator, nodes: revealjs_notes):  # noqa: D103
    if not isinstance(self.builder, RevealjsHTMLBuilder):
        self.visit_admonition(nodes)
        return
    self.body.append('<aside class="notes">')


def depart_revaljs_notes(self: SphinxTranslator, nodes: revealjs_notes):  # noqa: D103
    if not isinstance(self.builder, RevealjsHTMLBuilder):
        self.depart_admonition(nodes)
        return
    self.body.append("</aside>")


def setup(app: Sphinx):  # noqa: D103
    app.add_node(revealjs_notes, html=(visit_revealjs_notes, depart_revaljs_notes))
    app.add_directive("revealjs-notes", RevealjsNotes)
    return {
        "version": __version__,
        "env_version": 2,
        "parallel_read_safe": True,
    }
