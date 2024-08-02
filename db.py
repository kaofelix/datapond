from pathlib import Path

import duckdb
from qtpy.QtCore import QObject, Signal


class Table:
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name
        self.columns = self._get_columns()

    @classmethod
    def from_file(cls, conn, path):
        name = path.stem.replace("-", "_")
        conn.sql(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')")
        return cls(conn, name)

    def _get_columns(self):
        return self.conn.sql(
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            f"WHERE table_name = '{self.name}'"
        ).fetchall()


class DB(QObject):
    table_added = Signal(Table)
    table_dropped = Signal(Table)
    error_occurred = Signal(duckdb.Error)

    def __init__(self):
        super().__init__()
        self.conn = duckdb.connect()
        self.tables = []

    def create_tables_from_data_dir(self, data_dir: Path):
        for csv_path in data_dir.glob("*.csv"):
            try:
                self._add_table_from_file(csv_path)
            except duckdb.Error as e:
                self.error_occurred.emit(e)

    def sql(self, query):
        try:
            result = self.conn.sql(query)
            self._check_for_new_tables()
            return result
        except duckdb.Error as e:
            self.error_occurred.emit(e)

    def _add_table_from_file(self, path):
        table = Table.from_file(self.conn, path)
        self.tables.append(table)
        self.table_added.emit(table)
        return table

    def _check_for_new_tables(self):
        schema_table_names = set(self._db_schema_tables())
        tracked_table_names = {t.name for t in self.tables}

        if missing_tables := schema_table_names - tracked_table_names:
            for table in missing_tables:
                table = Table(self.conn, table)
                self.tables.append(table)
                self.table_added.emit(table)

        if extra_tables := tracked_table_names - schema_table_names:
            for table in extra_tables:
                table = next(t for t in self.tables if t.name == table)
                self.tables.remove(table)
                self.table_dropped.emit(table)

    def _db_schema_tables(self):
        return (
            i[0]
            for i in self.conn.sql(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        )
