import duckdb
from db import QueryResult, Table

from gui.resultview import ResultTable


def test_result_table_display_results(qtbot, datadir):
    conn = duckdb.connect()
    Table.from_file(conn, datadir / "people.csv")

    result = QueryResult(conn.sql("SELECT * FROM people"))

    table = ResultTable()
    table.show_result(result)
    qtbot.addWidget(table)

    assert table.rowCount() == 2
    assert table.columnCount() == 2
    assert table.horizontalHeaderItem(0).text() == "name"
    assert table.horizontalHeaderItem(1).text() == "age"
    assert table.item(0, 0).text() == "Alice"
    assert table.item(0, 1).text() == "25"
