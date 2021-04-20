import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
import uuid
from xml.etree import ElementTree

import lxml.etree
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor

from .database import Database

if (sys.version_info[0] >= 3) and (sys.version_info[1] >= 7):
    Match = re.Match
else:
    Match = Any

DEFAULT_PREAMBLE = [
    r"\documentclass[crop,border={2pt 0pt}]{standalone}",
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
    if svg is not None:
        return svg

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
                # "--output-format=dvi",
                texfile_path,
            ]
        )

        subprocess.check_output(["pdfcrop", "--hires", Path(working_dir) / "input.pdf"])

        # convert pdf to svg
        svgfile_path = working_dir / "output.svg"
        subprocess.check_output(["pdfcrop", Path(working_dir) / "input.pdf"])
        subprocess.check_output(
            [
                "dvisvgm",
                "--pdf",
                "--optimize=all",
                "--no-fonts",
                "--exact-bbox",
                f"--output={svgfile_path}",
                Path(working_dir) / "input.pdf",
            ]
        )

        with open(svgfile_path) as fptr:
            svg = fptr.read().strip()

        svg = lxml.etree.tostring(
            lxml.etree.fromstring(svg.encode(), parser=lxml.etree.ETCompatXMLParser())
        ).decode()

        shutil.rmtree(working_dir)

        db.add_equation(equation, svg)
        return svg

    except subprocess.CalledProcessError:
        print(f"error rendering formula, check job {equationid}", file=sys.stderr)
        return f"<code>${equation}$</code>"


class InlineMathProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        equation = m.group(1).strip()
        svg = render_svg(self.unescape(equation))
        element = ElementTree.Element("span")
        element.set("class", "math")
        element.text = self.md.htmlStash.store(svg)
        return element, m.start(0), m.end(0)


class DisplayMathProcessor(BlockProcessor):
    RE_START = re.compile(r"^\s*\$\$\s*\n")
    RE_END = re.compile(r"\n\s*\$\$\s*$")

    def test(self, parent, block):
        return self.RE_START.match(block)

    def run(self, parent, blocks):
        original_block = blocks[0]

        # remove starting fence
        blocks[0] = self.RE_START.sub("", blocks[0])

        for block_index, block in enumerate(blocks):
            if self.RE_END.search(block):
                # remove ending fence
                stripped_block = self.RE_END.sub("", block)
                blocks[block_index] = stripped_block

                element = ElementTree.SubElement(parent, "div")
                element.set("class", "math")
                element.text = self.parser.md.htmlStash.store(
                    render_svg(stripped_block.strip())
                )
                # self.parser.parseBlocks(element, blocks[0 : block_index + 1])

                for i in range(0, block_index + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False
