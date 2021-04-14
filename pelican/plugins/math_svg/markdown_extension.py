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
from markdown.util import AtomicString

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
            return svg

        except subprocess.CalledProcessError:
            print(f"error rendering formula, check job {equationid}", file=sys.stderr)
            return f"<code>${equation}$</code>"

    return None


class InlineMathProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        equation = m.group(1).strip()
        svg = render_svg(self.unescape(equation))
        element = Element("span")
        element.set("class", "math")
        element.text = AtomicString(svg)
        return element, m.start(0), m.end(0)
