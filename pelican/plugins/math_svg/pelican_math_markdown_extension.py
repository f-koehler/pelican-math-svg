import subprocess
from xml.etree.ElementTree import Element

import markdown

regex_math_inline = r"(?P<prefix>\$)(?P<math>.+?)(?P<suffix>(?<!\s)\2)"
regex_math_display = (
    r"(?P<prefix>\$\$|\\begin\{(.+?)\})(?P<math>.+?)(?P<suffix>\2|\\end\{\3\})"
)


class PelicanMathPattern(markdown.inlinepatterns.Pattern):
    def __init__(self, extension, tag, pattern):
        super().__init__(pattern)

        self.math_class = "math"
        self.pelican_math_extension = extension
        self.tag = tag

    def handleMatch(self, m):
        node = Element(self.tag)
        node.set("class", self.math_class)

        # prefix = "\\(" if m.group("prefix") == "$" else m.group("prefix")
        # suffix = "\\)" if m.group("suffix") == "$" else m.group("suffix")
        # node.text = markdown.util.AtomicString(prefix + m.group("math") + suffix)
        node.text = (
            subprocess.check_output(["tex2svg", m.group("math")]).decode().strip()
        )
        return node


class PelicanMathExtension(markdown.Extension):
    def __init__(self):
        super().__init__()

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            PelicanMathPattern(self, "div", regex_math_display), "math_displayed", 186
        )

        md.inlinePatterns.register(
            PelicanMathPattern(self, "span", regex_math_inline), "math_inlined", 185
        )
