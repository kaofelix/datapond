from unittest.mock import Mock

from utils import SignalOnChange


def test_signal_on_change_property():
    class MyClass:
        prop = SignalOnChange(int)

        def __init__(self, value):
            self.prop.value = value

    instance = MyClass(0)

    listener = Mock()
    instance.prop.changed.connect(listener)

    instance.prop.value = 2

    assert instance.prop.value == 2
    listener.assert_called_once_with(2)
