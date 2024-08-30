from unittest import mock

import pytest
from db import QueryResultModel
from polars import DataFrame
from qtpy.QtWidgets import QComboBox

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
    def test_sets_up_mapper_and_series(self, qtbot, query_result_model):
        mapper = SeriesMapper(query_result_model)
        qtbot.addWidget(mapper)

        assert items(mapper.x_column_combobox) == [
            "date",
            "value",
            "another_value",
        ]
        assert items(mapper.y_column_combobox) == [
            "date",
            "value",
            "another_value",
        ]

        assert mapper.x_column_combobox.currentText() == "date"
        assert mapper.y_column_combobox.currentText() == "value"

        assert mapper.mapper.xColumn() == 0
        assert mapper.mapper.yColumn() == 1

        assert mapper.mapper.model() is query_result_model

    def test_changes_mapping_when_changing_columns(self, qtbot, query_result_model):
        mapper = SeriesMapper(query_result_model)
        qtbot.addWidget(mapper)

        mapper.x_column_combobox.setCurrentIndex(1)
        mapper.y_column_combobox.setCurrentIndex(2)

        assert mapper.mapper.xColumn() == 1
        assert mapper.mapper.yColumn() == 2

    def test_swap_indexes_when_changed_to_same_column(self, qtbot, query_result_model):
        mapper = SeriesMapper(query_result_model)
        qtbot.addWidget(mapper)

        mapper.y_column_combobox.setCurrentIndex(0)

        assert mapper.mapper.xColumn() == 1
        assert mapper.mapper.yColumn() == 0

        mapper.x_column_combobox.setCurrentIndex(0)

        assert mapper.mapper.xColumn() == 0
        assert mapper.mapper.yColumn() == 1

    def test_emits_changed_signal_when_changing_columns(
        self, qtbot, query_result_model
    ):
        widget = SeriesMapper(query_result_model)
        widget.mapping_changed.connect(mapping_changed_mock := mock.Mock())
        qtbot.addWidget(widget)

        widget.y_column_combobox.setCurrentIndex(0)

        mapping_changed_mock.assert_called_once()


def items(combobox: QComboBox):
    return [combobox.itemText(i) for i in range(combobox.count())]
