from db import QueryResultModel
from qtpy.QtCharts import QChart, QChartView, QLineSeries, QVXYModelMapper
from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QWidget


def plot_result(query_results: QueryResultModel) -> QWidget:
    chart = QChart()

    series = QLineSeries()
    mapper = QVXYModelMapper()
    mapper.setXColumn(0)
    mapper.setYColumn(1)
    mapper.setSeries(series)
    mapper.setModel(query_results)

    chart.addSeries(series)
    chart.createDefaultAxes()
    chart.layout().setContentsMargins(0, 0, 0, 0)

    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

    chart_view.setWindowTitle("Plot Results")
    chart_view.resize(400, 300)
    chart_view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

    return chart_view
