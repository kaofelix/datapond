from unittest import mock

import pytest
from db import QueryResultModel
from polars import DataFrame
from qtpy.QtCharts import QChart

from gui.plotter import SeriesMapper


@pytest.fixture
def query_result_model():
    query_result_model = QueryResultModel()
    query_result_model.set_result(
        DataFrame(
            {
                "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
                "value": [1, 2, 3],
                "another_value": [4, 5, 6],
            }
        )
    )
    return query_result_model


class TestSeriesMapper:
    def test_binds_model_to_mapper(self, qtbot, query_result_model):
        series_mapper = SeriesMapper(query_result_model)
        qtbot.addWidget(series_mapper)

        assert series_mapper.mapper.model() is query_result_model

    def test_emits_changed_signal_when_changing_columns(
        self, qtbot, query_result_model
    ):
        series_mapper = SeriesMapper(query_result_model)
        series_mapper.mapping_changed.connect(mapping_changed_mock := mock.Mock())
        qtbot.addWidget(series_mapper)

        series_mapper.y_column_combobox.setCurrentIndex(0)
        series_mapper.x_column_combobox.setCurrentIndex(1)

        assert mapping_changed_mock.call_count == 2

    def test_maps_a_series_to_a_chart(self, qtbot, query_result_model):
        series_mapper = SeriesMapper(query_result_model)
        qtbot.addWidget(series_mapper)

        series_mapper.x_column_combobox.setCurrentIndex(1)
        series_mapper.y_column_combobox.setCurrentIndex(2)

        chart = QChart()
        series_mapper.map_to(chart)

        assert chart.series() == [series_mapper.mapper.series()]
