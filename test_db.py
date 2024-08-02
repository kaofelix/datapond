import shutil
from unittest import mock

import duckdb

from db import DB, Table


class TestDB:
    def test_create_tables_from_data_dir(self, datadir):
        db = DB()
        db.table_added.connect(table_added_signal_mock := mock.Mock())

        db.create_tables_from_data_dir(datadir)

        assert {"people", "animals"} <= {t.name for t in db.tables}

        people_table = next(t for t in db.tables if t.name == "people")
        assert {("name", "VARCHAR"), ("age", "BIGINT")} == set(people_table.columns)

        animals_table = next(t for t in db.tables if t.name == "animals")
        assert {("name", "VARCHAR"), ("species", "VARCHAR")} == set(
            animals_table.columns
        )

        assert table_added_signal_mock.call_count == 2

    def test_create_table_from_sql(self):
        db = DB()
        db.table_added.connect(table_added_signal_mock := mock.Mock())

        db.sql("CREATE TABLE new_table (a_column VARCHAR, another_column INTEGER)")

        assert "new_table" in {t.name for t in db.tables}
        new_table = next(t for t in db.tables if t.name == "new_table")
        assert {("a_column", "VARCHAR"), ("another_column", "INTEGER")} == set(
            new_table.columns
        )
        assert table_added_signal_mock.call_count == 1

    def test_delete_table_from_sql(self):
        db = DB()
        db.table_dropped.connect(table_deleted_signal_mock := mock.Mock())

        db.sql("CREATE TABLE new_table (a_column VARCHAR, another_column INTEGER)")
        db.sql("DROP TABLE new_table")

        assert "new_table" not in {t.name for t in db.tables}
        assert table_deleted_signal_mock.call_count == 1

    def test_signals_query_errors(self):
        db = DB()
        db.error_occurred.connect(error_occurred_signal_mock := mock.Mock())

        result = db.sql("SELECT * FROM non_existent_table")

        assert result is None
        assert error_occurred_signal_mock.call_count == 1

    def test_signals_errors_on_table_creation_from_directory(self, tmp_path):
        with open(tmp_path / "somefile.csv", "w") as f:
            f.write("anything")

        db = DB()
        db.error_occurred.connect(error_occurred_signal_mock := mock.Mock())

        with mock.patch("db.Table.from_file") as from_file_mock:
            from_file_mock.side_effect = duckdb.Error()
            db.create_tables_from_data_dir(tmp_path)

        assert error_occurred_signal_mock.call_count == 1


class TestTable:
    def test_from_file(self, datadir):
        conn = duckdb.connect()
        table = Table.from_file(conn, datadir / "people.csv")

        assert table.name == "people"
        assert {("name", "VARCHAR"), ("age", "BIGINT")} == set(table.columns)

    def test_from_file_with_dash(self, datadir, tmp_path):
        shutil.copy(datadir / "people.csv", tmp_path / "test-with-dash.csv")

        conn = duckdb.connect()
        table = Table.from_file(conn, tmp_path / "test-with-dash.csv")

        assert table.name == "test_with_dash"
