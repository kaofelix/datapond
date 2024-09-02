from typing import Callable

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QWidget,
)

from gui.layout import hbox


class IndexCombobox(QWidget):
    """Sets an index based on its list of items through a setter."""

    changed = Signal(int)

    def __init__(
        self,
        items: list[str],
        setter: Callable[[int], None],
        *,
        label_text: str,
        default_index: int = 0,
    ):
        super().__init__()

        self.label = QLabel(label_text)

        self.combobox = QComboBox()
        self.combobox.addItems(items)
        self.combobox.setCurrentIndex(default_index)
        self.combobox.currentIndexChanged.connect(self._set_and_emit(setter))
        setter(default_index)

        self.setLayout(hbox(self.label, (self.combobox, 1)))

    def _set_and_emit(self, setter):
        def index_changed(index):
            setter(index)
            self.changed.emit(index)

        return index_changed

    def setCurrentIndex(self, index):
        self.combobox.setCurrentIndex(index)

    def currentIndex(self):
        return self.combobox.currentIndex()

    def items(self):
        return [self.combobox.itemText(i) for i in range(self.combobox.count())]
