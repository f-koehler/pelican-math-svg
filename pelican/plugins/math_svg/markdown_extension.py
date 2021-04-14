import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Tuple, Union
import uuid
from xml.etree.ElementTree import Element

from markdown.inlinepatterns import InlineProcessor

from .database import Database

if (sys.version_info[0] >= 3) and (sys.version_info[1] >= 7):
    Match = re.Match
else:
    Match = Any

import markdown

DEFAULT_PREAMBLE = [
    r"\documentclass{standalone}",
    r"\usepackage{amsmath}",
    r"\usepackage{amssymb}",
]


def render_svg(math: str) -> str:
    path_shelf = Path(".cache") / "pelican-math-svg"
    path_shelf.parent.mkdir(exist_ok=True, parents=True)

    if os.environ.get("PELICAN_MATH_SVG_DRY", "FALSE").upper() == "FALSE":
        dry_mode = False
    else:
        dry_mode = True

    equation = math.strip()

    db = Database()
    svg = db.fetch_rendered_equation(equation)
    if svg is None:
        if dry_mode:
            db.add_equation(equation)
            return f"<code>${equation}$</code>"

        equationid = uuid.uuid4().hex
        working_dir = Path.cwd() / ".cache" / "pelican-math-svg" / "tmp" / equationid
        if working_dir.exists():
            shutil.rmtree(working_dir)
        working_dir.mkdir(parents=True)

        # generate LaTeX code
        code = DEFAULT_PREAMBLE + [
            r"\begin{document}",
            r"$\!",
            equation,
            r"$",
            r"\end{document}",
        ]

        # write LaTeX file
        texfile_path = working_dir / "input.tex"
        with open(texfile_path, "w") as fptr:
            fptr.write("\n".join(code))

        try:
            # render LaTeX to pdf file
            subprocess.check_output(
                [
                    "lualatex",
                    f"--output-directory={working_dir}",
                    "--interaction=errorstopmode",
                    "--halt-on-error",
                    "--output-format=dvi",
                    texfile_path,
                ]
            )

            # convert pdf to svg
            svgfile_path = working_dir / "output.svg"
            subprocess.check_output(
                [
                    "dvisvgm",
                    "--optimize=all",
                    "--no-fonts",
                    "--exact-bbox",
                    f"--output={svgfile_path}",
                    Path(working_dir) / "input.dvi",
                ]
            ).decode().strip()

            with open(svgfile_path) as fptr:
                svg = (
                    fptr.read()
                    .replace("<?xml version='1.0' encoding='UTF-8'?>", "")
                    .strip()
                )

            shutil.rmtree(working_dir)

            db.add_equation(equation, svg)
        except subprocess.CalledProcessError:
            print(f"error rendering formula, check job {equationid}", file=sys.stderr)
            return f"<code>${equation}$</code>"

    return svg


class InlineMathProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        equation = m.group(1).strip()
        svg = render_svg(equation)
        return Element(f'<span class="math">{svg}<span>'), m.start(0), m.end(0)


class InlineMathExtension(Extension):
    def extendMarkdown(self, md):


# class PelicanMathPattern(markdown.inlinepatterns.Pattern):
#     def __init__(self, extension, tag: str, pattern: str):
#         super().__init__(pattern)

#         self.math_class = "math"
#         self.pelican_math_extension = extension
#         self.tag = tag

#     def handleMatch(self, m: Match) -> Element:
#         node = Element(self.tag)
#         node.set("class", self.math_class)

#         prefix = "\\(" if m.group("prefix") == "$" else m.group("prefix")
#         suffix = "\\)" if m.group("suffix") == "$" else m.group("suffix")
#         node.text = markdown.util.AtomicString(prefix + m.group("math") + suffix)
#         node.text = render_svg(m.group("math"))
#         return node


# class PelicanMathFixDisplay(markdown.treeprocessors.Treeprocessor):
#     def __init__(self, extension):
#         self.math_class = "math"
#         self.pelican_math_extension = extension

#     def fix_display_math(
#         self,
#         root: Element,
#         children: List[Element],
#         math_divs: List[int],
#         insert_index: int,
#         text: Optional[str],
#     ):
#         current_index = 0
#         for index in math_divs:
#             element = Element("p")
#             element.text = text
#             element.extend(children[current_index:index])

#             if (len(element) != 0) or (element.text and not element.text.isspace()):
#                 root.insert(insert_index, element)
#                 insert_index += 1

#             text = children[index].tail
#             children[index].tail = None
#             root.insert(insert_index, children[index])
#             insert_index += 1
#             current_index = index + 1

#         element = Element("p")
#         element.text = text
#         element.extend(children[current_index:])

#         if (len(element) != 0) or (element.text and not element.text.isspace()):
#             root.insert(insert_index, element)

#     def run(self, root: Element) -> Element:
#         for parent in root:
#             math_divs = []
#             children = list(parent)

#             for div in parent.findall("div"):
#                 if div.get("class") == self.math_class:
#                     math_divs.append(children.index(div))

#             if not math_divs:
#                 continue

#             insert_idx = list(root).index(parent)
#             self.fix_display_math(root, children, math_divs, insert_idx, parent.text)
#             root.remove(parent)

#         return root
