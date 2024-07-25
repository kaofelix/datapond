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
        name = path.stem
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

    def __init__(self):
        super().__init__()
        self.conn = duckdb.connect()
        self.tables = []

    def create_tables_from_data_dir(self, data_dir: Path):
        for csv_path in data_dir.glob("*.csv"):
            self._add_table_from_file(csv_path)

    def sql(self, query):
        result = self.conn.sql(query)
        self._check_for_new_tables()
        return result

    def _add_table_from_file(self, path):
        table = Table.from_file(self.conn, path)
        self.tables.append(table)
        self.table_added.emit(table)
        return table

    def _check_for_new_tables(self):
        for table in self._table_names():
            if table not in (t.name for t in self.tables):
                table = Table(self.conn, table)
                self.tables.append(table)
                self.table_added.emit(table)

    def _table_names(self):
        return (
            i[0]
            for i in self.conn.sql(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        )
