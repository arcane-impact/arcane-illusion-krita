from enum import Enum
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressBar


class ProgressBar(QProgressBar):
    """Progress bar in busy mode with text displayed"""
    _text: Optional[str] = None

    class Color(Enum):
        Foreground = "#E2E2E2"
        Background = "#474747"
        DeepBackground = "#333333"
        Red = "#754343"
        Yellow = "#68633C"
        Green = "#437545"
        Blue = "#53728E"

    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def set_text(self, text):
        self._text = text

    def text(self):
        return self._text

    def set_busy(self, is_busy):
        if is_busy:
            self.setRange(0, 0)
            self.setValue(0)
        else:
            self.setRange(0, 100)
            self.setValue(100)

    def set_color(self, color: Color):
        if color:
            self.setStyleSheet(f"""
            QProgressBar {{
                color: {ProgressBar.Color.Foreground.value};
                background-color: {ProgressBar.Color.DeepBackground.value};
            }}
            QProgressBar::chunk {{
                background-color: {color.value};
                border: 1px solid {ProgressBar.Color.DeepBackground.value};
                border-radius: 2px;
            }}
            """.strip())
        else:
            self.setStyleSheet(None)
