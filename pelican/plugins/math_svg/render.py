from __future__ import annotations

import importlib.resources
import logging
import os
from pathlib import Path
import shutil
import subprocess
import uuid

import lxml.etree

from .database import Database
from .settings import PelicanMathSettings


def remove_svg_comments(code: str) -> str:
    return lxml.etree.tostring(
        lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser()),
    ).decode()


def remove_svg_pageid(code: str) -> str:
    doc = lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser())
    for element in doc.xpath(
        "//svg:g",
        namespaces={"svg": "http://www.w3.org/2000/svg"},
    ):
        if element.attrib.get("id", "") == "page1":
            element.attrib.pop("id")
    return lxml.etree.tostring(doc).decode()


def fix_strokeonly(code: str, css_class: str) -> str:
    doc = lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser())
    for element in doc.xpath(
        "//svg:path[@fill='none' and @stroke='#000']",
        namespaces={"svg": "http://www.w3.org/2000/svg"},
    ):
        element.attrib.pop("stroke")
        element.attrib["class"] = css_class
    return lxml.etree.tostring(doc).decode()


def add_title(code: str, equation: str) -> str:
    doc = lxml.etree.fromstring(code.encode(), parser=lxml.etree.ETCompatXMLParser())
    title = lxml.etree.SubElement(doc, "title")
    title.text = f"${equation}$"
    return lxml.etree.tostring(doc).decode()


def run_scour(
    code: str,
    args: list[str],
    logger: logging.Logger = logging.getLogger(__name__ + ".run_scour"),
) -> str:
    logger.debug("Run scour")
    cmd = ["scour"] + args
    result = (
        subprocess.check_output(
            cmd,
            input=code.encode(),
        )
        .decode()
        .strip()
    )
    logger.debug("Finished running scour")
    return result


def run_svgo(
    code: str,
    args: list[str],
    titles: bool,
    logger: logging.Logger = logging.getLogger(__name__ + ".run_svgo"),
) -> str:
    if not titles:
        logger.debug("Run svgo")
        cmd = ["svgo", "--input", "-", "--output", "-"] + args
        logger.debug(f"{cmd = }")
        result = (
            subprocess.check_output(
                cmd,
                input=code.encode(),
            )
            .decode()
            .strip()
        )
        logger.debug("Finished running svgo")
        return result

    with importlib.resources.path("pelican.plugins.math_svg", "svgo.js") as svgo_config:
        logger.debug("Run svgo")
        cmd = [
            "svgo",
            "--input",
            "-",
            "--output",
            "-",
            "--config",
            str(svgo_config),
        ] + args
        logger.debug(f"{cmd = }")
        result = (
            subprocess.check_output(
                cmd,
                input=code.encode(),
            )
            .decode()
            .strip()
        )
        logger.debug("Finished running svgo")
        return result


def render_svg(math: str, inline: bool, settings: PelicanMathSettings) -> str:
    logger = logging.getLogger(__name__ + ".render_svg")

    if os.environ.get("PELICAN_MATH_SVG_DRY", "FALSE").upper() == "FALSE":
        dry_mode = False
    else:
        dry_mode = True

    equation = math.strip()

    db = Database()
    svg, settings_string = db.fetch_rendered_equation(inline, equation)
    if (svg is not None) and (settings_string == settings.serialize()):
        logger.debug("Equation up-to-date")
        return svg

    if dry_mode:
        logger.debug("Add unrendered equation to DB")
        db.add_equation(inline, equation, settings)
        return f"<code>${equation}$</code>"

    equationid = uuid.uuid4().hex
    working_dir = Path.cwd() / ".cache" / "pelican-math-svg" / "tmp" / equationid
    if working_dir.exists():
        shutil.rmtree(working_dir)
    working_dir.mkdir(parents=True)

    handler = logging.FileHandler(working_dir / "render.log")
    handler.setLevel(logging.DEBUG)

    # generate LaTeX code
    if inline:
        math_open = r"\("
        math_close = r"\)"
    else:
        math_open = r"\("
        math_close = r"\)"

    code = settings.latex_preamble + [
        r"\begin{document}",
        math_open,
        equation,
        math_close,
        r"\end{document}",
    ]

    # write LaTeX file
    texfile_path = working_dir / "input.tex"
    with open(texfile_path, "w") as fptr:
        fptr.write("\n".join(code))

    try:
        # render LaTeX to pdf file
        logger.debug("Rendering LaTeX")
        cmd = (
            [
                settings.latex_program,
                f"--output-directory={working_dir}",
            ]
            + settings.latex_args
            + [
                str(texfile_path),
            ]
        )
        logger.debug(f"{cmd = }")
        output = subprocess.check_output(cmd).decode()
        for line in output.splitlines():
            logger.debug(line)
        logger.debug("Finished rendering LaTeX")

        logger.debug("Cropping PDF")
        cmd = (
            ["pdfcrop"] + settings.pdfcrop_args + [str(Path(working_dir) / "input.pdf")]
        )
        logger.debug(f"{cmd = }")
        output = subprocess.check_output(cmd).decode()
        for line in output.splitlines():
            logger.debug(line)
        logger.debug("Finished cropping PDF")

        # convert pdf to svg
        svgfile_path = working_dir / "output.svg"
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

        logger.debug("Convert PDF to SVG")
        cmd = (
            [
                "dvisvgm",
            ]
            + settings.dvisvgm_args
            + scale_args
            + [
                f"--output={svgfile_path}",
                str(Path(working_dir) / "input-crop.pdf"),
            ]
        )
        env = os.environ.copy()
        env["GS_OPTIONS"] = "-dNEWPDF=false"
        logger.debug(f"{cmd = }")
        output = subprocess.check_output(cmd, env=env).decode()
        for line in output.splitlines():
            logger.debug(line)
        logger.debug("Finished converting PDF to SVG")

        with open(svgfile_path) as fptr:
            svg = fptr.read().strip()

        logging.info("Remove SVG comments")
        svg = remove_svg_comments(svg)

        logging.info("Remove SVG pageid")
        svg = remove_svg_pageid(svg)

        logging.info("Fix strokeonly class")
        svg = fix_strokeonly(svg, settings.strokeonly_class)

        if settings.titles:
            logger.debug("Add title to SVG")
            svg = add_title(svg, equation)

        if settings.scour:
            svg = run_scour(svg, settings.scour_args, logger)

        if settings.svgo:
            svg = run_svgo(svg, settings.svgo_args, settings.titles, logger)

        logger.removeHandler(handler)
        handler.close()
        logger.debug("Remove working directory")
        shutil.rmtree(working_dir)

        logger.debug("Store rendered equation")
        db.add_equation(inline, equation, settings, svg)
        return svg

    except subprocess.CalledProcessError as e:
        logger.error(f"error rendering formula, check job {equationid}")
        logger.error(f"{e.cmd = }")
        logger.error(f"{e.returncode = }")
        logger.error(f"{e.stderr = }")
        return f"<code>${equation}$</code>"
