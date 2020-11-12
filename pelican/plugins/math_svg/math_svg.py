import logging
import shutil
import re
import subprocess

import pelican.plugins.signals
import pelican.generators

log = logging.getLogger(__name__)
path_tex2svg = None

regex_inline = re.compile(r"\$\$((?:.|\n)+?)(?<!\\)\$\$")


def check_prerequisites(sender):
    global path_tex2svg
    path_tex2svg = shutil.which("tex2svg")

    if not path_tex2svg:
        log.error("failed to find tex2svg in path, disable LaTeX math processing")


def process_content(generators):
    if not path_tex2svg:
        return

    for generator in generators:
        if isinstance(generator, pelican.generators.ArticlesGenerator):
            for article in (
                generator.articles + generator.translations + generator.drafts
            ):
                render_math(article)
        elif isinstance(generator, pelican.generators.PagesGenerator):
            for page in generator.pages + generator.hidden_pages:
                render_math(page)


def render_math(page):
    def replace(match):
        return subprocess.check_output([path_tex2svg, match.group(1)]).decode().strip()

    page._content = regex_inline.sub(replace, page._content)


def register():
    pelican.plugins.signals.initialized.connect(check_prerequisites)
    pelican.plugins.signals.all_generators_finalized.connect(process_content)
