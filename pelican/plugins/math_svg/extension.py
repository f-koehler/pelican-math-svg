import markdown

from .markdown_extension import DisplayMathProcessor, InlineMathProcessor
from .settings import PelicanMathSettings


class PelicanMathExtension(markdown.Extension):
    def __init__(self, settings: PelicanMathSettings):
        super().__init__()

        self.settings = settings

    def extendMarkdown(self, md: markdown.core.Markdown):
        md.inlinePatterns.register(
            InlineMathProcessor(
                r"(?<!\\|\$)\$((?:[^$]|\\\$)+)(?<!\\)\$(?!\$)",
                self.settings,
                md,
            ),
            "inline_math",
            200,
        )
        md.parser.blockprocessors.register(
            DisplayMathProcessor(self.settings, md.parser),
            "display_math",
            200,
        )
