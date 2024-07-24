import pytest

from main import MainWindow

data_csv = """
name,age
Alice,25
Bob,30
"""


@pytest.fixture
def app_window(qtbot, tmp_path):
    with open(tmp_path / "data.csv", "w") as f:
        f.write(data_csv)

    app_window = MainWindow(data_dir=tmp_path)
    qtbot.addWidget(app_window)
    yield app_window


def test_display_some_data(app_window: MainWindow):
    app_window.query_line_edit.setText("select * from data")
    app_window.submit_query_button.click()

    assert app_window.results_table.rowCount() == 2
    assert app_window.results_table.columnCount() == 2
    assert app_window.results_table.item(0, 0).text() == "Alice"
    assert app_window.results_table.item(0, 1).text() == "25"


def test_shows_tables_in_tree(app_window: MainWindow):
    assert app_window.tables_tree.topLevelItemCount() == 1
    assert app_window.tables_tree.topLevelItem(0).text(0) == "data"
    assert app_window.tables_tree.topLevelItem(0).childCount() == 2
