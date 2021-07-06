from __future__ import annotations

import json
import shutil
from typing import Any

import pkg_resources

from pelican import Pelican


class PelicanMathSettings:
    def __init__(self):
        self.plugin_version: str = pkg_resources.get_distribution(
            "pelican-math-svg"
        ).version

        self.scour: bool = True if shutil.which("scour") else False
        self.scour_args: list[str] = [
            "--strip-xml-prolog",
            "--remove-titles",
            "--remove-descriptions",
            "--remove-metadata",
            "--remove-descriptive-elements",
            "--enable-comment-stripping",
            "--strip-xml-space",
            "--enable-id-stripping",
        ]
        self.svgo: bool = True if shutil.which("svgo") else False
        self.svgo_args: list[str] = ["--multipass", "--precision", "5"]

    def serialize(self) -> str:
        obj: dict[str, Any] = {
            "plugin_version": self.plugin_version,
            "scour": self.scour,
            "svgo": self.svgo,
        }
        if self.scour:
            obj["scour_args"] = self.scour_args

        if self.svgo_args:
            obj["svgo_args"] = self.svgo_args

        return json.dumps(obj)

    @staticmethod
    def from_settings(pelican: Pelican) -> PelicanMathSettings:
        obj = PelicanMathSettings()
        settings = pelican.settings.get("MATH_SVG", None)

        if settings is None:
            return obj

        if "scour" in settings:
            obj.scour = True
            if isinstance(settings["scour"], dict):
                obj.scour_args = settings["scour"].get("args", obj.scour_args)

        if "svgo" in settings:
            obj.scour = True
            if isinstance(settings["svgo"], dict):
                obj.scour_args = settings["svgo"].get("args", obj.scour_args)

        return obj
