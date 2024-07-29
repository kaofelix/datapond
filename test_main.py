from pathlib import Path

import pytest
from qtpy.QtWidgets import QFileDialog

from main import MainWindow

DATA_CSV = """
name,age
Alice,25
Bob,30
"""


@pytest.fixture
def create_data_file(tmp_path):
    def _create_data_file(file_name, contents) -> Path:
        p = tmp_path / file_name

        with open(p, "w") as f:
            f.write(contents)

        return p

    return _create_data_file


@pytest.fixture
def app_window(qtbot):
    app_window = MainWindow()
    qtbot.addWidget(app_window)
    yield app_window


def test_load_tables_from_directory_data_source(
    app_window: MainWindow, create_data_file, monkeypatch
):
    path = create_data_file("data.csv", DATA_CSV)

    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", classmethod(lambda *_: str(path.parent))
    )

    app_window.add_dir_data_source_action.trigger()

    app_window.query_line_edit.setText("select * from data")
    app_window.submit_query_button.click()

    assert app_window.results_table.rowCount() == 2
    assert app_window.results_table.columnCount() == 2
    assert app_window.results_table.item(0, 0).text() == "Alice"
    assert app_window.results_table.item(0, 1).text() == "25"

    assert app_window.tables_tree.topLevelItemCount() == 1
    assert app_window.tables_tree.topLevelItem(0).text(0) == "data"
    assert app_window.tables_tree.topLevelItem(0).childCount() == 2


def test_created_table_shows_up_in_tree(app_window: MainWindow):
    app_window.query_line_edit.setText("CREATE TABLE new_table (name TEXT, age INT)")
    app_window.submit_query_button.click()

    assert app_window.tables_tree.topLevelItemCount() == 1
    assert app_window.tables_tree.topLevelItem(0).text(0) == "new_table"
    assert app_window.tables_tree.topLevelItem(0).childCount() == 2
