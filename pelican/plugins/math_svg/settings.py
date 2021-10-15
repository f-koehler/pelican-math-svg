from __future__ import annotations

import json
import shutil
from typing import Any

import pkg_resources

from pelican import Pelican


class PelicanMathSettings:
    def __init__(self):
        self.plugin_version: str = pkg_resources.get_distribution(
            "pelican-math-svg",
        ).version

        self.titles: bool = True

        self.scale_display: float | tuple[float, float] = 1.0
        self.scale_inline: float | tuple[float, float] = 1.0

        self.strokeonly_class: str = "strokeonly"

        self.latex_preamble: list[str] = [
            r"\documentclass[preview,border={2pt 0pt}]{standalone}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
        ]
        self.latex_program: str = "lualatex"
        self.latex_args: list[str] = ["--interaction=errorstopmode", "--halt-on-error"]

        self.dvisvgm_args: list[str] = [
            "--pdf",
            "--optimize=all",
            "--no-fonts",
            "--exact-bbox",
        ]

        self.pdfcrop_args: list[str] = [
            "--hires",
        ]

        self.scour: bool = True if shutil.which("scour") else False
        self.scour_args: list[str] = [
            "--strip-xml-prolog",
            "--remove-descriptions",
            "--remove-metadata",
            "--enable-comment-stripping",
            "--strip-xml-space",
            "--enable-id-stripping",
        ]
        self.svgo: bool = True if shutil.which("svgo") else False
        self.svgo_args: list[str] = ["--multipass", "--precision", "5"]

    def serialize(self) -> str:
        obj: dict[str, Any] = {
            "plugin_version": self.plugin_version,
            "titles": self.titles,
            "scale_inline": self.scale_inline,
            "scale_display": self.scale_display,
            "strokeonly_class": self.strokeonly_class,
            "latex": {
                "args": self.latex_args,
                "preamble": self.latex_preamble,
                "program": self.latex_program,
            },
            "pdfcrop": {
                "args": self.pdfcrop_args,
            },
            "dvisvgm": {
                "args": self.dvisvgm_args,
            },
            "scour": {"enabled": self.scour},
            "svgo": {"enabled": self.svgo},
        }
        if self.scour:
            obj["scour"]["args"] = self.scour_args

        if self.svgo_args:
            obj["svgo"]["args"] = self.svgo_args

        return json.dumps(obj)

    @staticmethod
    def from_settings(pelican: Pelican) -> PelicanMathSettings:
        obj = PelicanMathSettings()
        settings = pelican.settings.get("MATH_SVG", None)

        if settings is None:
            return obj

        obj.titles = settings.get("titles", obj.titles)

        obj.scale_inline = settings.get("scale_inline", obj.scale_inline)
        obj.scale_display = settings.get("scale_display", obj.scale_display)

        obj.strokeonly_class = settings.get("strokeonly_class", obj.strokeonly_class)

        if "scour" in settings:
            obj.scour = settings["scour"].get("enabled", obj.scour)
            obj.scour_args = settings["scour"].get("args", obj.scour_args)

        if "svgo" in settings:
            obj.svgo = settings["svgo"].get("enabled", obj.svgo)
            obj.svgo_args = settings["svgo"].get("args", obj.svgo_args)

        return obj
