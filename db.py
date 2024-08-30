from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import duckdb
from polars import DataFrame
from qtpy.QtCore import QAbstractTableModel, QObject, Qt, Signal


@dataclass
class Table:
    name: str
    columns: list

    @classmethod
    def from_file(cls, conn, path):
        name = path.stem.replace("-", "_")
        conn.sql(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')")
        columns = cls._get_columns(conn, name)
        return cls(name, columns)

    @classmethod
    def from_existing(cls, conn, name):
        return Table(name, cls._get_columns(conn, name))

    @staticmethod
    def _get_columns(conn: duckdb.DuckDBPyConnection, name):
        return conn.sql(
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            f"WHERE table_name = '{name}'"
        ).fetchall()


class DB(QObject):
    table_added = Signal(Table)
    table_dropped = Signal(Table)
    error_occurred = Signal(duckdb.Error)

    schema_tracker: "SchemaTracker"
    result_model: "QueryResultModel"

    def __init__(self, conn, schema_tracker, result_model):
        super().__init__()
        self._conn = conn
        self.result_model = result_model
        self.schema_tracker = schema_tracker
        self.schema_tracker.table_added.connect(self.table_added.emit)
        self.schema_tracker.table_dropped.connect(self.table_dropped.emit)

    @classmethod
    def from_connection(cls):
        conn = duckdb.connect()
        return cls(conn, SchemaTracker(conn), QueryResultModel())

    @property
    def tables(self):
        return self.schema_tracker.tables

    def create_tables_from_data_dir(self, data_dir: Path):
        for csv_path in data_dir.glob("*.csv"):
            try:
                name = csv_path.stem.replace("-", "_")
                self._conn.sql(
                    f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{csv_path}')"
                )
                self.schema_tracker.refresh()
            except duckdb.Error as e:
                self.error_occurred.emit(e)

    def sql(self, query) -> Optional[DataFrame]:
        try:
            result = self._conn.sql(query)
            self.schema_tracker.refresh()
            if result:
                self.result_model.set_result(result.pl())
        except duckdb.Error as e:
            self.error_occurred.emit(e)


class SchemaTracker(QObject):
    table_added = Signal(Table)
    table_dropped = Signal(Table)

    tables: list[Table]

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        super().__init__()
        self._conn = conn
        self.tables = []

    def refresh(self):
        schema_table_names = set(self._db_schema_tables())
        tracked_table_names = {t.name for t in self.tables}

        if missing_tables := schema_table_names - tracked_table_names:
            for table in missing_tables:
                table = Table.from_existing(self._conn, table)
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
            for i in self._conn.sql(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        )


class QueryResultModel(QAbstractTableModel):
    result: DataFrame

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = DataFrame()

    def set_result(self, result: DataFrame):
        self.beginResetModel()
        self.result = result
        self.endResetModel()

    @property
    def column_names(self):
        return self.result.columns

    def rowCount(self, parent=None):
        return self.result.shape[0]

    def columnCount(self, parent=None):
        return self.result.shape[1]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.result.columns[section]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.result[index.row(), index.column()]
