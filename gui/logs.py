from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTextEdit


class LogPanel(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_exception(self, e: Exception):
        default_color = self.textColor()
        self.setTextColor(Qt.GlobalColor.red)
        self.append(str(e))
        self.setTextColor(default_color)
