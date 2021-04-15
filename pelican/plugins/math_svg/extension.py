import markdown

from .markdown_extension import DisplayMathProcessor, InlineMathProcessor


class PelicanMathExtension(markdown.Extension):
    def __init__(self):
        super().__init__()

    def extendMarkdown(self, md: markdown.core.Markdown):
        md.inlinePatterns.register(
            InlineMathProcessor(r"(?<!\\|\$)\$((?:[^$]|\\\$)+)(?<!\\)\$(?!\$)", md),
            "inline_math",
            200,
        )
        md.parser.blockprocessors.register(
            DisplayMathProcessor(md.parser), "display_math", 200
        )
