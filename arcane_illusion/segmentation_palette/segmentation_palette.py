from typing import ClassVar

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QComboBox, QCompleter, QListView, QSizePolicy

from krita import DockWidget, Krita, ManagedColor

from .segmentation_classes import CLASSES


class ClassComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMinimumWidth(200)
        list_view = QListView()
        list_view.setWordWrap(True)
        self.setView(list_view)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        self.currentIndexChanged.connect(self.on_index_changed)

    def add_class(self, c):
        color = QColor(c.r, c.g, c.b)
        pixmap = QPixmap(64, 64)
        pixmap.fill(color)
        icon = QIcon(pixmap)
        self.addItem(icon, c.name, color)

    def add_classes(self, classes):
        for c in classes:
            self.add_class(c)

    @pyqtSlot(int)
    def on_index_changed(self, index):
        color = self.itemData(index)
        active_window = Krita.instance().activeWindow()
        active_view = active_window and active_window.activeView()
        if active_view:
            managed_color = ManagedColor.fromQColor(color)
            active_view.setForeGroundColor(managed_color)


class SegmentationPalette(DockWidget):
    id: ClassVar[str] = 'segmentation_palette'

    def __init__(self):
        super().__init__()
        self._build_interface()

    def _build_interface(self):
        self.setWindowTitle("AI - Segmentation Palette")
        combobox = ClassComboBox()
        combobox.add_classes(CLASSES)
        combobox.setCurrentIndex(-1)
        self.setWidget(combobox)

    def canvasChanged(self, canvas):
        pass
