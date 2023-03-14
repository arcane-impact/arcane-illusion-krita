import sys
from PyQt5.QtWidgets import QMenu, QWidget, QMessageBox

from krita import Krita, Extension, DockWidget

from .constants import EXTENSION_ID, EXTENSION_NAME, EXTENSION_VERSION


class ArcaneIllusion(Extension):

    def __init__(self, parent):
        super().__init__(parent)
        self.window = None
        self.krita = Krita.instance()

    def setup(self):
        pass

    def createActions(self, window):
        menu_location = f"tools/{EXTENSION_ID}"

        action = window.createAction(EXTENSION_ID, EXTENSION_NAME, "tools")
        action.setMenu(QMenu(EXTENSION_ID, window.qwindow()))

        about = window.createAction(self._build_action_id("about"), "About", menu_location)
        about.triggered.connect(self._about_triggered)

    @staticmethod
    def _build_action_id(action_id):
        return f"{EXTENSION_ID}_{action_id}"

    def _about_triggered(self):
        text = f"""
        {EXTENSION_NAME} version: {EXTENSION_VERSION}
        Python version: {'.'.join(map(str, sys.version_info))}
        Krita version: {Application.version()}
        """
        QMessageBox.information(QWidget(), f"About {EXTENSION_NAME}", text)
