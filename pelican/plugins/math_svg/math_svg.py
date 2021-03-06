import pelican.plugins.signals

from .extension import PelicanMathExtension


def init_math(sender):
    sender.settings["MARKDOWN"].setdefault("extensions", []).append(
        PelicanMathExtension()
    )


def register():
    pelican.plugins.signals.initialized.connect(init_math)
