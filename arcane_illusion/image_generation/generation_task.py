from typing import Callable, TypeVar, Generic

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal, pyqtSlot

T = TypeVar("T")


class Signals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)


class GenerationTask(QRunnable, Generic[T]):
    signals: Signals

    def __init__(self, task: Callable[[], T]):
        super().__init__()
        self.signals = Signals()
        self._task = task

    def run(self):
        try:
            self.signals.started.emit()
            self.signals.finished.emit(self._task())
        except Exception as e:
            self.signals.error.emit(e)
