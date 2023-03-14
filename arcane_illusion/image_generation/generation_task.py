import platform
from typing import Callable, TypeVar, Generic

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal, pyqtSlot

from arcane_illusion.image_generation.response import ProgressResponse

T = TypeVar("T")


class Signals(QObject):
    started = pyqtSignal()
    progress = pyqtSignal(object)
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


class Slots(QObject):
    task_started = False
    task_stopped = False

    @pyqtSlot()
    def on_task_started(self):
        self.task_started = True

    @pyqtSlot()
    def on_task_stopped(self):
        self.task_stopped = True


class ProgressTask(QRunnable):
    signals: Signals
    slots: Slots

    def __init__(self, generation_task: GenerationTask, progress_task):
        super().__init__()
        self.signals = Signals()
        self.slots = Slots()
        self._task = progress_task
        generation_task.signals.started.connect(self.slots.on_task_started)
        generation_task.signals.finished.connect(self.slots.on_task_stopped)
        generation_task.signals.error.connect(self.slots.on_task_stopped)

    def run(self):
        while not self.slots.task_started:
            QThread.currentThread().sleep(1)
        while not self.slots.task_stopped:
            if platform.system() == 'Darwin':
                self.signals.progress.emit(ProgressResponse(0, -1))
            else:
                self.signals.progress.emit(self._task())
            QThread.currentThread().sleep(1)
