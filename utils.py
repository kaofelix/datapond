from qtpy.QtCore import QObject, Signal

NOT_SET = object()


class SignalOnChange[T](QObject):
    changed: Signal

    def __init__(self, t: type[T], *, default: T = NOT_SET):
        super().__init__()
        self._value = t() if default is NOT_SET else default
        type(self).changed = Signal(t)

    def __set__(self, obj, value: T):
        raise AttributeError("Use the .value property to set the value")

    def __get__(self, obj, owner):
        return self

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T):
        self._value = value
        self.changed.emit(value)
