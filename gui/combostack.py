from qtpy.QtWidgets import QComboBox, QLabel, QStackedLayout, QWidget

from gui.layout import hbox, vbox


class ComboStack(QWidget):
    def __init__(self, label_text: str, parent=None):
        super().__init__(parent)
        label = QLabel()
        label.setText(label_text)

        self.combobox = QComboBox()
        self.stack = QStackedLayout()

        self.setLayout(
            vbox(
                hbox(label, (self.combobox, 1)),
                self.stack,
            )
        )
        self.combobox.currentIndexChanged.connect(self.stack.setCurrentIndex)

    def add_widget(self, name, widget):
        self.combobox.addItem(name)
        widget.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(widget)
