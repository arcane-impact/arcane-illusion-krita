import base64
from typing import ClassVar

from PyQt5.QtCore import QObject, QByteArray, QThreadPool, pyqtSlot, pyqtSignal, qWarning, qInfo
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QPushButton

from krita import Krita, DockWidget

from arcane_illusion.settings import Parameters
from .generation_task import GenerationTask
from .client import Client
from .common_parameters import CommonParameters
from .response import GenerationResponse
from .status import Status
from .status_bar import StatusBar


class _Widget(QWidget):
    _thread_pool: QThreadPool = QThreadPool.globalInstance()
    status_updated = pyqtSignal([Status], [Status, str])

    def __init__(self):
        super().__init__()
        self._parameters = Parameters()
        self._client = Client()
        self._build_ui()
        self._connect_ui()
        self._load_options()

    def _build_ui(self):
        self.setWindowTitle("AI - Image Generation")
        layout = QVBoxLayout()

        self._status_bar = StatusBar(self)
        layout.addWidget(self._status_bar)

        self._common_parameters = CommonParameters(self._parameters)
        layout.addWidget(self._common_parameters)

        self._generate_button = QPushButton("Generate", self)
        layout.addWidget(self._generate_button)

        layout.addStretch(0)

        self.setLayout(layout)

    def _load_options(self):
        try:
            self._parameters.load()
            self.status_updated.emit(Status.Loading)
            self._common_parameters.update_model_options(self._client.get_models())
            self._common_parameters.update_sampler_options(self._client.get_samplers())
            self._common_parameters.populate_parameters()
            self.status_updated.emit(Status.Ready)
        except OSError as e:
            qWarning(repr(e))
            self.status_updated.emit(Status.Error, "Cannot connect to API")

    def _connect_ui(self):
        self._generate_button.clicked.connect(self._generate)
        self.status_updated.connect(self._on_status_change)
        self.status_updated.connect(self._status_bar.update)

    def _generate(self):
        if not Krita.instance().activeDocument():
            QMessageBox.warning(QWidget(), "Warning", "No active document.")
            return
        self._parameters.save()
        task = GenerationTask(lambda: self._client.generate(self._parameters.as_dict()))
        task.signals.started.connect(self._on_task_started)
        task.signals.finished.connect(self._on_task_finished)
        task.signals.error.connect(self._on_task_error)
        self._thread_pool.start(task)

    @pyqtSlot()
    def _on_task_started(self):
        self.status_updated.emit(Status.Processing)

    @pyqtSlot(GenerationResponse)
    def _on_task_finished(self, response: GenerationResponse):
        try:
            application = Krita.instance()
            doc = application.activeDocument()
            root = doc.rootNode()
            prompt = response.parameters["prompt"]
            qInfo(f"Image generated with {str(response.parameters)}")
            for index, encoded in enumerate(response.images):
                buffer = QByteArray.fromRawData(base64.b64decode(encoded))
                image = QImage.fromData(buffer)
                ptr = image.bits()
                ptr.setsize(image.byteCount())
                layer = doc.createNode("_".join(map(str, [prompt, index])), "paintlayer")
                layer.setPixelData(QByteArray(ptr.asstring()), 0, 0, image.width(), image.height())
                root.addChildNode(layer, None)
            doc.refreshProjection()
            self.status_updated.emit(Status.Ready)
        except Exception as e:
            qWarning(repr(e))
            self.status_updated.emit(Status.Error, str(e))

    @pyqtSlot(Status)
    @pyqtSlot(Status, str)
    def _on_status_change(self, status: Status):
        self._generate_button.setEnabled(status == Status.Ready or status == Status.Error)

    @pyqtSlot(Exception)
    def _on_task_error(self, e: Exception):
        qWarning(repr(e))
        self.status_updated.emit(Status.Error, str(e))


class ImageGeneration(DockWidget):
    id: ClassVar[str] = "image_generation"

    def __init__(self):
        super().__init__()
        self.setWidget(_Widget())

    def canvasChanged(self, canvas):
        pass
