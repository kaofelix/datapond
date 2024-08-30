from qtpy.QtWidgets import QWidget

from gui.combostack import ComboStack


def test_combostack(qtbot):
    combostack = ComboStack("Choose a widget")
    qtbot.addWidget(combostack)

    combostack.add_widget("widget1", widget1 := QWidget())
    combostack.add_widget("widget2", widget2 := QWidget())

    assert combostack.stack.currentWidget() is widget1

    combostack.combobox.setCurrentIndex(1)

    assert combostack.stack.currentWidget() is widget2
