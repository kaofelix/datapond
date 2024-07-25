import duckdb
import pytest

from db import Table


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
