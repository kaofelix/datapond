from db import QueryResultModel
from qtpy.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QScatterSeries,
    QVXYModelMapper,
)
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QWidget,
)

from gui.combostack import ComboStack
from gui.layout import hbox, vbox


class SeriesMapper(QWidget):
    mapping_changed = Signal()

    def __init__(self, result_model: QueryResultModel):
        super().__init__()

        self.mapper = QVXYModelMapper()
        self.mapper.setModel(result_model)

        x_label, self.x_column_combobox = self._column_combobox("X", result_model)
        self.x_column_combobox.setCurrentIndex(0)
        self.mapper.setXColumn(self.x_column_combobox.currentIndex())

        self.x_column_combobox.currentIndexChanged.connect(self._on_x_column_changed)

        y_label, self.y_column_combobox = self._column_combobox("Y", result_model)
        self.y_column_combobox.setCurrentIndex(1)
        self.mapper.setYColumn(self.y_column_combobox.currentIndex())

        self.y_column_combobox.currentIndexChanged.connect(self._on_y_column_changed)

        self.setLayout(
            hbox(
                x_label,
                self.x_column_combobox,
                y_label,
                self.y_column_combobox,
            )
        )

    def _column_combobox(self, axis: str, result_model: QueryResultModel):
        label = QLabel(f"{axis} Column")
        combobox = QComboBox()
        for col in result_model.column_names:
            combobox.addItem(col)
        return label, combobox

    def _on_x_column_changed(self, index):
        if index == self.mapper.yColumn():
            self.y_column_combobox.blockSignals(True)
            self.y_column_combobox.setCurrentIndex(self.mapper.xColumn())
            self.mapper.setYColumn(self.mapper.xColumn())
            self.y_column_combobox.blockSignals(False)

        self.mapper.setXColumn(index)
        self.mapping_changed.emit()

    def _on_y_column_changed(self, index):
        if index == self.mapper.xColumn():
            self.x_column_combobox.blockSignals(True)
            self.x_column_combobox.setCurrentIndex(self.mapper.yColumn())
            self.mapper.setXColumn(self.mapper.yColumn())
            self.x_column_combobox.blockSignals(False)

        self.mapper.setYColumn(index)
        self.mapping_changed.emit()


class ScatterSeriesMapper(SeriesMapper):
    @property
    def series(self):
        series = QScatterSeries()
        self.mapper.setSeries(series)
        return series


class ModelChart(QWidget):
    def __init__(self, series_mapper: SeriesMapper):
        super().__init__()
        self.series_mapper = series_mapper
        self.chart = QChart()
        self._add_series_to_chart(self.series_mapper, self.chart)

        self.series_mapper.mapping_changed.connect(
            lambda: self._add_series_to_chart(self.series_mapper, self.chart)
        )

        self.chart_view = QChartView()
        self.chart_view.viewport().setAttribute(
            Qt.WidgetAttribute.WA_AcceptTouchEvents, False
        )
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setLayout(vbox(self.series_mapper, self.chart_view))

    def _add_series_to_chart(self, series_mapper, chart):
        series = QLineSeries()
        series_mapper.mapper.setSeries(series)
        chart.removeAllSeries()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.layout().setContentsMargins(0, 0, 0, 0)


class Plotter(ComboStack):
    PLOT_TO_MAPPER_WIDGET = {
        "Line": SeriesMapper,
        "Scatter": ScatterSeriesMapper,
    }

    plot_type_combobox: QComboBox

    def __init__(self, result_model: QueryResultModel):
        super().__init__("Plot type: ")
        self.result_model = result_model
        for plot_name, mapper_widget_type in self.PLOT_TO_MAPPER_WIDGET.items():
            self.add_widget(plot_name, ModelChart(mapper_widget_type(result_model)))


def plot_result(query_results: QueryResultModel) -> QWidget:
    plotter = Plotter(query_results)

    plotter.setWindowTitle("Plot Results")
    plotter.resize(800, 600)

    return plotter
