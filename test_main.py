from pytestqt.qt_compat import qt_api

from main import MainWindow

data_csv = """
name,age
Alice,25
Bob,30
"""


def test_display_some_data(qtbot, tmp_path):
    with open(tmp_path / "data.csv", "w") as f:
        f.write(data_csv)

    app_window = MainWindow(data_dir=tmp_path)
    qtbot.addWidget(app_window)

    app_window.query_line_edit.setText("select * from data")
    app_window.submit_query_button.click()

    path = qtbot.screenshot(app_window)
    qt_api.qWarning(f"Screenshot saved to {path}")

    assert app_window.results_table.rowCount() == 1
    assert app_window.results_table.columnCount() == 2
    assert app_window.results_table.item(0, 0).text() == "Alice"
    assert app_window.results_table.item(0, 1).text() == "25"
