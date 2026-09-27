from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from lv_chordia_lab.config.logging_config import configure_logging
from lv_chordia_lab.config.settings import Settings
from lv_chordia_lab.ui.main_window import MainWindow
from lv_chordia_lab.ui.theme import apply_application_theme


def main() -> int:
    settings = Settings.from_environment()
    configure_logging(settings.log_level)

    app = QApplication(sys.argv)
    app.setApplicationName("LV Chordia Lab")
    app.setOrganizationName("LVChordiaLab")
    apply_application_theme(app)

    window = MainWindow(settings=settings)
    window.show()

    return app.exec()
