import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import lxml.etree

from .database import Database
from .settings import PelicanMathSettings


def remove_svg_comments(code: str) -> str:
    return lxml.etree.tostring(
        lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser())
    ).decode()


def remove_svg_pageid(code: str) -> str:
    doc = lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser())
    for element in doc.xpath(
        "//svg:g", namespaces={"svg": "http://www.w3.org/2000/svg"}
    ):
        if element.attrib.get("id", "") == "page1":
            element.attrib.pop("id")
    return lxml.etree.tostring(doc).decode()


def run_scour(code: str, args: list[str]) -> str:
    return (
        subprocess.check_output(
            [
                "scour",
            ]
            + args,
            input=code.encode(),
        )
        .decode()
        .strip()
    )


def run_svgo(code: str, args: list[str]) -> str:
    return (
        subprocess.check_output(
            ["svgo", "--input", "-", "--output", "-"] + args, input=code.encode()
        )
        .decode()
        .strip()
    )


def render_svg(inline: bool, math: str, settings: PelicanMathSettings) -> str:
    path_shelf = Path(".cache") / "pelican-math-svg"
    path_shelf.parent.mkdir(exist_ok=True, parents=True)

    if os.environ.get("PELICAN_MATH_SVG_DRY", "FALSE").upper() == "FALSE":
        dry_mode = False
    else:
        dry_mode = True

    equation = math.strip()

    db = Database()
    svg, settings_string = db.fetch_rendered_equation(inline, equation)
    if (svg is not None) and (settings_string == settings.serialize()):
        return svg

    if dry_mode:
        db.add_equation(equation, settings)
        return f"<code>${equation}$</code>"

    equationid = uuid.uuid4().hex
    working_dir = Path.cwd() / ".cache" / "pelican-math-svg" / "tmp" / equationid
    if working_dir.exists():
        shutil.rmtree(working_dir)
    working_dir.mkdir(parents=True)

    # generate LaTeX code
    code = settings.latex_preamble + [
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
                settings.latex_program,
                f"--output-directory={working_dir}",
            ]
            + settings.latex_args
            + [
                str(texfile_path),
            ]
        )

        subprocess.check_output(
            [
                "pdfcrop",
            ]
            + settings.pdfcrop_args
            + [
                str(Path(working_dir) / "input.pdf"),
            ]
        )

        # convert pdf to svg
        svgfile_path = working_dir / "output.svg"
        subprocess.check_output(["pdfcrop", Path(working_dir) / "input.pdf"])

        if inline:
            scale = settings.scale_inline
        else:
            scale = settings.scale_display
        scale_args = []
        if scale != 1.0:
            if isinstance(scale, tuple):
                scale_args = [
                    f"--scale={scale[0]},{scale[1]}",
                ]
            else:
                scale_args = [
                    f"--scale={scale}",
                ]
        subprocess.check_output(
            [
                "dvisvgm",
            ]
            + settings.dvisvgm_args
            + scale_args
            + [
                f"--output={svgfile_path}",
                str(Path(working_dir) / "input.pdf"),
            ]
        )

        with open(svgfile_path) as fptr:
            svg = fptr.read().strip()

        svg = remove_svg_comments(svg)
        svg = remove_svg_pageid(svg)

        if settings.scour:
            svg = run_scour(svg, settings.scour_args)

        if settings.svgo:
            svg = run_svgo(svg, settings.svgo_args)

        shutil.rmtree(working_dir)

        db.add_equation(inline, equation, settings, svg)
        return svg

    except subprocess.CalledProcessError:
        print(f"error rendering formula, check job {equationid}", file=sys.stderr)
        return f"<code>${equation}$</code>"
