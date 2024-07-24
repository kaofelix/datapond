from qtpy.QtWidgets import QTreeWidgetItem


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


class TableTreeItem(QTreeWidgetItem):
    def __init__(self, table):
        super().__init__([table.name])
        for column, data_type in table.columns:
            self.addChild(QTreeWidgetItem([f"{column} {data_type}"]))
