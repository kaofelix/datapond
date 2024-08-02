import duckdb
from db import Table

from tabletree import TableTreeItem


def test_table_tree_item(datadir):
    conn = duckdb.connect()

    table = Table.from_file(conn, datadir / "people.csv")
    tree_item = TableTreeItem(table)

    assert tree_item.childCount() == 2
    assert tree_item.child(0).text(0) == "name"
    assert tree_item.child(0).text(1) == "VARCHAR"
    assert tree_item.child(1).text(0) == "age"
    assert tree_item.child(1).text(1) == "BIGINT"
