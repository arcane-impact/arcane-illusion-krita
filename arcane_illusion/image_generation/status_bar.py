from PyQt5.QtCore import pyqtSlot

from arcane_illusion.widgets import ProgressBar
from .status import Status


class StatusBar(ProgressBar):

    @pyqtSlot(Status)
    @pyqtSlot(Status, str)
    def update(self, status: Status, message: str = None):
        if status == Status.Ready:
            self.set_color(ProgressBar.Color.Green)
            self.set_text("Ready")
            self.set_busy(False)
        elif status == Status.Error:
            self.set_color(ProgressBar.Color.Red)
            self.set_text(message)
            self.set_busy(False)
        elif status == Status.Processing:
            self.set_color(ProgressBar.Color.Blue)
            self.set_text("Processing...")
            self.set_busy(True)
        else:
            self.set_color(ProgressBar.Color.Yellow)
            self.set_text("Loading...")
            self.set_busy(True)
