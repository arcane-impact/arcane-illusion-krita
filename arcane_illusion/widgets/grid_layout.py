from PyQt5.QtWidgets import QWidget, QGridLayout


class AutoGridLayout(QGridLayout):
    def __init__(self):
        super().__init__()
        self._row = 0
        self._col = 0

    def add_widget(self, widget: QWidget, column_span: int = 1):
        self.addWidget(widget, self._row, self._col, 1, column_span)
        self._col += column_span

    def end_row(self):
        self._row += 1
        self._col = 0
