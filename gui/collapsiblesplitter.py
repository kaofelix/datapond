from typing import cast

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSplitter, QWidget


class CollapsibleSplitter(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Vertical)
        self._original_positions = {}

    def add(self, widget, stretch=0, collapsible=True):
        self.addWidget(widget)
        self.setStretchFactor(self.count() - 1, stretch)
        self.setCollapsible(self.count() - 1, collapsible)

    def toggle_collapsed(self, widget: QWidget):
        index = self.indexOf(widget)
        assert index != -1, "Widget not found in splitter"

        handle = self.handle(index)
        _, max = cast(tuple[int, int], self.getRange(index))

        if widget.height() > 0:
            self._original_positions[index] = handle.pos().y()
            handle.moveSplitter(max)
        else:
            handle.moveSplitter(self._original_positions.get(index, 0))
