from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPlainTextEdit, QSizePolicy, QSpinBox, QDoubleSpinBox

from arcane_illusion.settings import Parameters
from arcane_illusion.widgets import AutoGridLayout


class CommonParameters(QWidget):
    def __init__(self, parameters: Parameters):
        super().__init__()
        self._parameters = parameters
        self._build()
        self._connect()

    def _build(self):
        layout = AutoGridLayout()

        layout.add_widget(QLabel("Model"))
        self._model = QComboBox()
        layout.add_widget(self._model, 3)
        layout.end_row()

        self._prompt = QPlainTextEdit()
        self._prompt.setPlaceholderText("Place your prompt here")
        self._prompt.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.add_widget(QLabel("Prompt"))
        layout.add_widget(self._prompt, 3)
        layout.end_row()

        self._negative_prompt = QPlainTextEdit()
        self._negative_prompt.setPlaceholderText("Place your negative prompt here")
        self._negative_prompt.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.add_widget(QLabel("Negative\nPrompt"))
        layout.add_widget(self._negative_prompt, 3)
        layout.end_row()

        self._sampler = QComboBox()
        layout.add_widget(QLabel("Sampler"))
        layout.add_widget(self._sampler)
        self._steps = QSpinBox()
        self._steps.setRange(1, 150)
        layout.add_widget(QLabel("Steps"))
        layout.add_widget(self._steps)
        layout.end_row()

        self._width = QSpinBox()
        self._width.setSingleStep(8)
        self._width.setRange(64, 2048)
        layout.add_widget(QLabel("Width"))
        layout.add_widget(self._width)

        self._height = QSpinBox()
        self._height.setSingleStep(8)
        self._height.setRange(64, 2048)
        layout.add_widget(QLabel("Height"))
        layout.add_widget(self._height)
        layout.end_row()

        self._seed = QSpinBox()
        self._seed.setRange(-2147483648, 2147483647)
        layout.add_widget(QLabel("Seed"))
        layout.add_widget(self._seed)

        self._cfg_scale = QDoubleSpinBox()
        self._cfg_scale.setDecimals(1)
        self._cfg_scale.setSingleStep(0.5)
        self._cfg_scale.setRange(1, 30)
        layout.addWidget(QLabel("CFG Scale"))
        layout.addWidget(self._cfg_scale)
        layout.end_row()

        self.setLayout(layout)

    def _connect(self):
        self._prompt.textChanged.connect(lambda: setattr(self._parameters, "prompt", self._prompt.toPlainText()))
        self._negative_prompt.textChanged.connect(
            lambda: setattr(self._parameters, "negative_prompt", self._negative_prompt.toPlainText()))
        self._model.currentTextChanged.connect(lambda model: setattr(self._parameters, "sd_model", model))
        self._sampler.currentTextChanged.connect(lambda sampler: setattr(self._parameters, "sampler", sampler))
        self._steps.valueChanged.connect(lambda steps: setattr(self._parameters, "steps", steps))
        self._width.valueChanged.connect(lambda width: setattr(self._parameters, "width", width))
        self._height.valueChanged.connect(lambda height: setattr(self._parameters, "height", height))
        self._seed.valueChanged.connect(lambda seed: setattr(self._parameters, "seed", seed))
        self._cfg_scale.valueChanged.connect(lambda cfg_scale: setattr(self._parameters, "cfg_scale", cfg_scale))

    def update_model_options(self, options):
        self._model.blockSignals(True)
        self._model.clear()
        self._model.addItems(options)
        self._model.blockSignals(False)

    def update_sampler_options(self, options):
        self._sampler.blockSignals(True)
        self._sampler.clear()
        self._sampler.addItems(options)
        self._sampler.blockSignals(False)

    def populate_parameters(self):
        self._model.setCurrentText(getattr(self._parameters, "sd_model"))
        self._prompt.setPlainText(getattr(self._parameters, "prompt"))
        self._negative_prompt.setPlainText(getattr(self._parameters, "negative_prompt"))
        self._sampler.setCurrentText(getattr(self._parameters, "sampler"))
        self._steps.setValue(getattr(self._parameters, "steps"))
        self._width.setValue(getattr(self._parameters, "width"))
        self._height.setValue(getattr(self._parameters, "height"))
        self._seed.setValue(getattr(self._parameters, "seed"))
        self._cfg_scale.setValue(getattr(self._parameters, "cfg_scale"))
