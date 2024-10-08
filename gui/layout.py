from typing import Type

from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QVBoxLayout,
    QWidget,
)


def hbox(*widgets):
    return _layout(QHBoxLayout, *widgets)


def vbox(*items):
    return _layout(QVBoxLayout, *items)


def _layout(cls: Type[QHBoxLayout | QVBoxLayout], *items):
    layout = cls()
    for item in items:
        match item:
            case QLayout() as l:
                layout.addLayout(l)
            case (QLayout() as l, int(stretch)):
                layout.addLayout(l, stretch)
            case QWidget() as w:
                layout.addWidget(w)
            case (QWidget() as w, int(stretch)):
                layout.addWidget(w, stretch)
            case str(text):
                layout.addWidget(QLabel(text))
            case (str(text), int(stretch)):
                layout.addWidget(QLabel(text), stretch)
    return layout
