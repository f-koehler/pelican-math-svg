import markdown

from .markdown_extension import PelicanMathFixDisplay, PelicanMathPattern

regex_math_inline = r"(?P<prefix>\$)(?P<math>.+?)(?P<suffix>(?<!\s)\2)"
regex_math_display = (
    r"(?P<prefix>\$\$|\\begin\{(.+?)\})(?P<math>.+?)(?P<suffix>\2|\\end\{\3\})"
)


class PelicanMathExtension(markdown.Extension):
    def __init__(self):
        super().__init__()

    def extendMarkdown(self, md: markdown.core.Markdown):
        md.inlinePatterns.register(
            PelicanMathPattern(self, "div", regex_math_display), "math_displayed", 186
        )

        md.inlinePatterns.register(
            PelicanMathPattern(self, "span", regex_math_inline), "math_inlined", 185
        )

        md.treeprocessors.register(
            PelicanMathFixDisplay(self), "math_correct_displayed", 15
        )
