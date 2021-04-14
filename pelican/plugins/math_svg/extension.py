import markdown

from .markdown_extension import InlineMathProcessor

regex_math_inline = r"(?P<prefix>\$)(?P<math>.+?)(?P<suffix>(?<!\s)\2)"
regex_math_display = (
    r"(?P<prefix>\$\$|\\begin\{(.+?)\})(?P<math>.+?)(?P<suffix>\2|\\end\{\3\})"
)


class PelicanMathExtension(markdown.Extension):
    def __init__(self):
        super().__init__()

    def extendMarkdown(self, md: markdown.core.Markdown):
        md.inlinePatterns.register(
            InlineMathProcessor(r"(?<!\\)\$((?:[^$]|\\\$)+)(?<!\\)\$", md),
            "inline_math",
            200,
        )