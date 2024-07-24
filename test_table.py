import duckdb
import pytest

from table import Table, TableTreeItem


@pytest.fixture
def data_csv(tmp_path):
    data_csv = """
name,age
Alice,25
Bob,30
"""
    data_csv_path = tmp_path / "data.csv"
    with open(data_csv_path, "w") as f:
        f.write(data_csv)

    return data_csv_path


def test_create_table_from_file(data_csv):
    conn = duckdb.connect()

    table = Table.from_file(conn, data_csv)

    assert conn.sql("select * from data").fetchall() == [("Alice", 25), ("Bob", 30)]
    assert table.name == "data"
    assert table.columns[0] == ("name", "VARCHAR")
    assert table.columns[1] == ("age", "BIGINT")


def test_table_tree_item(data_csv):
    conn = duckdb.connect()

    table = Table.from_file(conn, data_csv)
    tree_item = TableTreeItem(table)

    assert tree_item.childCount() == 2
    assert tree_item.child(0).text(0) == "name VARCHAR"
    assert tree_item.child(1).text(0) == "age BIGINT"
