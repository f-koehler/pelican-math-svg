from pelican import Pelican
import pelican.plugins.signals

from .extension import PelicanMathExtension
from .settings import PelicanMathSettings


def init_math(sender: Pelican):
    settings = PelicanMathSettings.from_settings(sender)
    sender.settings["MARKDOWN"].setdefault("extensions", []).append(
        PelicanMathExtension(settings)
    )


def register():
    pelican.plugins.signals.initialized.connect(init_math)
