from db import QueryResultModel
from qtpy.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QScatterSeries,
    QVXYModelMapper,
    QXYSeries,
)
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QWidget

from gui.combostack import ComboStack
from gui.indexcombobox import IndexCombobox
from gui.layout import hbox, vbox


class SeriesMapper(QWidget):
    mapping_changed = Signal()

    def __init__(self, result_model: QueryResultModel):
        super().__init__()

        self.mapper = QVXYModelMapper()
        self.mapper.setModel(result_model)

        self.x_column_combobox = IndexCombobox(
            result_model.column_names,
            self.mapper.setXColumn,
            label_text="X Column",
        )
        self.x_column_combobox.changed.connect(self.mapping_changed)

        self.y_column_combobox = IndexCombobox(
            result_model.column_names,
            self.mapper.setYColumn,
            label_text="Y Column",
            default_index=1,
        )
        self.y_column_combobox.changed.connect(self.mapping_changed)

        self.setLayout(
            hbox(
                self.x_column_combobox,
                self.y_column_combobox,
            )
        )

    def _create_series(self) -> QXYSeries:
        return QLineSeries()

    def map_to(self, chart):
        series = self._create_series()
        self.mapper.setSeries(series)
        chart.removeAllSeries()
        chart.addSeries(series)
        chart.createDefaultAxes()


class ScatterSeriesMapper(SeriesMapper):
    def _create_series(self):
        return QScatterSeries()


class ModelChart(QWidget):
    def __init__(self, mapper_widget: SeriesMapper):
        super().__init__()
        self.mapper_widget = mapper_widget
        self.chart = QChart()
        self.mapper_widget.map_to(self.chart)

        self.mapper_widget.mapping_changed.connect(
            lambda: self.mapper_widget.map_to(self.chart)
        )

        self.chart_view = QChartView()
        self.chart_view.setDragMode(QChartView.DragMode.ScrollHandDrag)
        self.chart_view.viewport().setAttribute(
            Qt.WidgetAttribute.WA_AcceptTouchEvents, False
        )
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setLayout(vbox(self.mapper_widget, self.chart_view))


class Plotter(ComboStack):
    PLOT_TO_MAPPER_WIDGET = {
        "Line": SeriesMapper,
        "Scatter": ScatterSeriesMapper,
    }

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
