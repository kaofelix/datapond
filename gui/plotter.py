import pyqtgraph as pg
from db import QueryResult
from qtpy.QtWidgets import QMainWindow, QWidget


def plot_result(query_results: QueryResult) -> QWidget:
    df = query_results._relation.fetchnumpy()

    plot_window = QMainWindow()
    plot_window.setWindowTitle("Plot Results")
    plot_window.resize(400, 300)

    plot_widget = pg.PlotWidget(plot_window, name="Results")
    plot_window.setCentralWidget(plot_widget)

    plot = plot_widget.plot()
    plot.setData(x=df[query_results.columns[0]], y=df[query_results.columns[1]])

    return plot_window


if __name__ == "__main__":
    import sys

    import duckdb
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    conn = duckdb.connect()
    rel = conn.sql("select * from 'data/numbers.csv'")

    window = plot_result(QueryResult(rel))
    window.show()
    sys.exit(app.exec_())
