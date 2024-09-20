from polars import DataFrame
from pyqtgraph import PlotDataItem, PlotWidget
from qtpy.QtWidgets import QComboBox, QWidget

from gui.combostack import ComboStack
from gui.layout import hbox, vbox


class XYChart(QWidget):
    def __init__(self, df: DataFrame, plot_type="Line"):
        super().__init__()
        self.df = df
        self.plot_widget = PlotWidget()
        self.plot_type = plot_type

        self.x_combobox = QComboBox()
        self.x_combobox.addItems(df.columns)
        self.x_combobox.setCurrentText(df.columns[0])
        self.x_combobox.currentTextChanged.connect(self.refresh_plot)

        self.y_combobox = QComboBox()
        self.y_combobox.addItems(df.columns)
        self.y_combobox.setCurrentText(df.columns[1])
        self.y_combobox.currentTextChanged.connect(self.refresh_plot)
        self.refresh_plot()

        self.setLayout(
            vbox(
                hbox(
                    hbox("X: ", (self.x_combobox, 2)),
                    hbox("Y: ", (self.y_combobox, 2)),
                ),
                self.plot_widget,
            )
        )

    def refresh_plot(self):
        kwargs = (
            {"pen": "w"} if self.plot_type == "Line" else {"symbol": "o", "pen": None}
        )

        self.plot_widget.clear()
        self.plot_widget.addItem(
            PlotDataItem(
                self.df[self.x_combobox.currentText()],
                self.df[self.y_combobox.currentText()],
                **kwargs,
            )
        )


class Plotter(ComboStack):
    PLOT_TYPES = [
        "Line",
        "Scatter",
    ]

    def __init__(self, df: DataFrame):
        super().__init__("Plot type: ")
        for plot_name in self.PLOT_TYPES:
            self.add_widget(plot_name, XYChart(df, plot_name))


def plot_result(df: DataFrame) -> QWidget:
    plotter = Plotter(df)

    plotter.setWindowTitle("Plot Results")
    plotter.resize(800, 600)

    return plotter


if __name__ == "__main__":
    import random
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    df = DataFrame(
        {
            "value": range(1000),
            "another_value": [random.randint(0, 100) for _ in range(1000)],
        }
    )

    widget = plot_result(df)
    widget.show()

    sys.exit(app.exec_())
