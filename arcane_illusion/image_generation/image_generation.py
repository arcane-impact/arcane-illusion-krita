import base64
from enum import Enum
from typing import ClassVar

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QComboBox, QMessageBox, \
    QProgressBar, QPushButton, QSpinBox, QFormLayout, QScrollArea, QPlainTextEdit, QDoubleSpinBox
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QThreadPool, QRunnable, pyqtSlot, qDebug

from arcane_illusion.image_generation.generation_task import GenerationTask, ProgressTask
from krita import Krita, DockWidget

from arcane_illusion.settings import Parameters
from arcane_illusion.image_generation.client import Client
from arcane_illusion.image_generation.response import GenerationResponse, ProgressResponse


class Status(Enum):
    Loading = "Loading"
    Ready = "Ready"
    Processing = "Processing"
    Error = "Error"


class ImageGeneration(DockWidget):
    id: ClassVar[str] = "image_generation"
    _status: Status = Status.Loading
    _thread_pool: QThreadPool = QThreadPool.globalInstance()

    def __init__(self):
        super().__init__()
        self._parameters = Parameters()
        self._client = Client()
        self._load_options()
        self._build_ui()
        self._restore_ui()
        self._update_ui()
        self._connect_ui()

    def _build_ui(self):
        self.setWindowTitle("AI - Image Generation")

        self.widget = QWidget(self)
        self.widget.setLayout(QVBoxLayout())
        # self.widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setWidget(self.widget)

        self.widget.layout().addLayout(self._build_ui_primary_layout())
        self.widget.layout().addWidget(self._build_ui_parameters_widget())

        self.generate_button = QPushButton("Generate", self)
        self.widget.layout().addWidget(self.generate_button)

    def _build_ui_primary_layout(self):
        primary_layout = QFormLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setTextVisible(True)

        primary_layout.addRow("Status", self.progress_bar)

        self.model = QComboBox()
        primary_layout.addRow("Model", self.model)

        self.prompt = QPlainTextEdit()
        self.prompt.setPlaceholderText("Place your prompt here")
        primary_layout.addRow("Prompt", self.prompt)

        self.negative = QPlainTextEdit()
        self.negative.setPlaceholderText("Place your negative prompt here")
        primary_layout.addRow("Negative", self.negative)

        return primary_layout

    def _build_ui_parameters_widget(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        grid_layout = QGridLayout()
        scroll_widget.setLayout(grid_layout)

        self.sampler = QComboBox()
        grid_layout.addWidget(QLabel("Sampler"), 0, 0)
        grid_layout.addWidget(self.sampler, 0, 1)
        self.sampling_steps = QSpinBox()
        self.sampling_steps.setRange(1, 150)
        grid_layout.addWidget(QLabel("Steps"), 1, 0)
        grid_layout.addWidget(self.sampling_steps, 1, 1)

        self.canvas_width = QSpinBox()
        self.canvas_width.setSingleStep(8)
        self.canvas_width.setRange(64, 2048)
        grid_layout.addWidget(QLabel("Width"), 0, 2)
        grid_layout.addWidget(self.canvas_width, 0, 3)

        self.canvas_height = QSpinBox()
        self.canvas_height.setSingleStep(8)
        self.canvas_height.setRange(64, 2048)
        grid_layout.addWidget(QLabel("Height"), 1, 2)
        grid_layout.addWidget(self.canvas_height, 1, 3)

        self.seed = QSpinBox()
        self.seed.setRange(-2147483648, 2147483647)
        grid_layout.addWidget(QLabel("Seed"), 2, 0)
        grid_layout.addWidget(self.seed, 2, 1)

        self.cfg_scale = QDoubleSpinBox()
        self.cfg_scale.setDecimals(1)
        self.cfg_scale.setSingleStep(0.5)
        self.cfg_scale.setRange(1, 30)
        grid_layout.addWidget(QLabel("CFG Scale"), 2, 2)
        grid_layout.addWidget(self.cfg_scale, 2, 3)

        return scroll_area

    def _load_options(self):
        try:
            self._parameters.load()
            self._status = Status.Loading
            self.models = self._client.get_models()
            self.samplers = self._client.get_samplers()
            self._status = Status.Ready
        except OSError:
            self.models = []
            self.samplers = []
            self._status = Status.Error

    def _update_status(self):
        if self._status == Status.Ready:
            self.progress_bar.setFormat(Status.Ready.value)
            self.progress_bar.setValue(100)
            self.progress_bar.setMaximum(100)
        elif self._status == Status.Error:
            self.progress_bar.setFormat(Status.Error.value)
        elif self._status == Status.Processing:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(self.progress)
            self.progress_bar.setFormat(f"%p% ({self.eta}s)")
        else:
            self.progress_bar.setMaximum(0)
            self.progress_bar.resetFormat()

    def _update_generate_button(self):
        self.generate_button.setEnabled(self._status == Status.Ready or self._status == Status.Error)

    def _restore_ui(self):
        self.prompt.setPlainText(self._parameters.prompt)
        self.negative.setPlainText(self._parameters.negative_prompt)
        self.model.clear()
        self.model.addItems(self.models)
        self.model.setCurrentText(self._parameters.sd_model)
        self.sampler.clear()
        self.sampler.addItems(self.samplers)
        self.sampler.setCurrentText(self._parameters.sampler)
        self.sampling_steps.setValue(self._parameters.steps)
        self.canvas_width.setValue(self._parameters.width)
        self.canvas_height.setValue(self._parameters.height)
        self.seed.setValue(self._parameters.seed)
        self.cfg_scale.setValue(self._parameters.cfg_scale)

    def _update_ui(self):
        self._update_status()
        self._update_generate_button()

    def _connect_ui(self):
        self.prompt.textChanged.connect(lambda: setattr(self._parameters, "prompt", self.prompt.toPlainText()))
        self.negative.textChanged.connect(lambda: setattr(self._parameters, "negative_prompt", self.negative.toPlainText()))
        self.model.currentTextChanged.connect(lambda model: setattr(self._parameters, "sd_model", model))
        self.sampler.currentTextChanged.connect(lambda sampler: setattr(self._parameters, "sampler", sampler))
        self.sampling_steps.valueChanged.connect(lambda steps: setattr(self._parameters, "steps", steps))
        self.canvas_width.valueChanged.connect(lambda width: setattr(self._parameters, "width", width))
        self.canvas_height.valueChanged.connect(lambda height: setattr(self._parameters, "height", height))
        self.seed.valueChanged.connect(lambda seed: setattr(self._parameters, "seed", seed))
        self.cfg_scale.valueChanged.connect(lambda cfg_scale: setattr(self._parameters, "cfg_scale", cfg_scale))
        self.generate_button.clicked.connect(self._generate)

    def _generate(self):
        if not Krita.instance().activeDocument():
            QMessageBox.warning(QWidget(), "Warning", "No active document.")
            return
        self._parameters.save()
        task = GenerationTask(lambda: self._client.generate(self._parameters.as_dict()))
        task.signals.started.connect(self._on_task_started)
        task.signals.finished.connect(self._on_task_finished)
        task.signals.error.connect(self._on_task_error)
        progress_task = ProgressTask(task, self._client.progress)
        progress_task.signals.progress.connect(self._on_task_progress)
        self._thread_pool.start(task)
        self._thread_pool.start(progress_task)

    @pyqtSlot()
    def _on_task_started(self):
        self._status = Status.Processing
        self.progress = 0
        self.eta = -1
        self._update_ui()

    @pyqtSlot(ProgressResponse)
    def _on_task_progress(self, response: ProgressResponse):
        self.progress = int(response.progress * 100)
        self.eta = int(response.eta_relative)
        self._update_ui()

    @pyqtSlot(GenerationResponse)
    def _on_task_finished(self, response: GenerationResponse):
        try:
            application = Krita.instance()
            doc = application.activeDocument()
            root = doc.rootNode()
            prompt = response.parameters["prompt"]
            qDebug(str(response.parameters))
            for index, encoded in enumerate(response.images):
                buffer = QByteArray.fromRawData(base64.b64decode(encoded))
                image = QImage.fromData(buffer)
                ptr = image.bits()
                ptr.setsize(image.byteCount())
                layer = doc.createNode("_".join(map(str, [prompt, index])), "paintlayer")
                layer.setPixelData(QByteArray(ptr.asstring()), 0, 0, image.width(), image.height())
                root.addChildNode(layer, None)
            doc.refreshProjection()
            self._status = Status.Ready
        except RuntimeError:
            self._status = Status.Error
        finally:
            self._update_ui()

    @pyqtSlot(Exception)
    def _on_task_error(self, e: Exception):
        self._status = Status.Error
        self._update_ui()

    def canvasChanged(self, canvas):
        pass
