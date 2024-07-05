import sys
from pathlib import Path

from qfluentwidgets import (qconfig, QConfig, ConfigItem, BoolValidator, Theme)


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """
    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())


YEAR = 2024
AUTHOR = "rudymohammadbali"
VERSION = "0.0.0"
HELP_URL = "https://github.com/rudymohammadbali/"
FEEDBACK_URL = "https://github.com/rudymohammadbali/"
RELEASE_URL = "https://github.com/rudymohammadbali/"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
cfg.micaEnabled.value = False
cfg.themeColor.value = "#07575b"
qconfig.load(Path(__file__).parent / "config" / "config.json", cfg)
