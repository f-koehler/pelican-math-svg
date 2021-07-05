import pelican.plugins.signals
from pelican import Pelican

from .extension import PelicanMathExtension
from .settings import PelicanMathSettings


def init_math(sender: Pelican):
    sender.settings["MARKDOWN"].setdefault("extensions", []).append(
        PelicanMathExtension()
    )
    settings = PelicanMathSettings.from_settings(sender)


def register():
    pelican.plugins.signals.initialized.connect(init_math)
