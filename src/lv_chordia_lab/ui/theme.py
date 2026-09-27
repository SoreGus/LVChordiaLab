from __future__ import annotations

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


def apply_application_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(_stylesheet())


def _stylesheet() -> str:
    return """
    QWidget {
        font-size: 14px;
    }

    QMainWindow {
        background: palette(window);
    }

    QPushButton {
        min-height: 34px;
        padding: 0 16px;
        border-radius: 9px;
        border: 1px solid palette(mid);
        background: palette(button);
    }

    QPushButton:hover {
        background: palette(midlight);
    }

    QPushButton:pressed {
        background: palette(mid);
    }

    QPushButton#PrimaryButton {
        font-weight: 600;
    }

    QFrame#Card {
        border: 1px solid palette(mid);
        border-radius: 14px;
        background: palette(base);
    }

    QLabel#Title {
        font-size: 24px;
        font-weight: 700;
    }

    QLabel#Subtitle {
        color: palette(mid);
    }

    QProgressBar {
        border: none;
        background: palette(midlight);
        border-radius: 4px;
        min-height: 8px;
        max-height: 8px;
    }

    QProgressBar::chunk {
        border-radius: 4px;
        background: palette(highlight);
    }

    QSlider::groove:horizontal {
        height: 5px;
        border-radius: 2px;
        background: palette(midlight);
    }

    QSlider::handle:horizontal {
        width: 15px;
        margin: -5px 0;
        border-radius: 7px;
        background: palette(highlight);
    }
    """


def is_dark_palette(app: QApplication) -> bool:
    color = app.palette().color(QPalette.ColorRole.Window)
    return color.lightness() < 128
