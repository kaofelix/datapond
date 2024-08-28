import shutil
from pathlib import Path
from typing import Callable

import duckdb
import pytest


@pytest.fixture
def conn():
    return duckdb.connect()


@pytest.fixture
def datadir(tmp_path, request):
    shutil.copytree(request.config.rootdir / "data", tmp_path / "data")
    return tmp_path / "data"


@pytest.fixture
def duck_relation(
    datadir: Path, conn: duckdb.DuckDBPyConnection
) -> Callable[[str], duckdb.DuckDBPyRelation]:
    def _duck_relation(filename):
        return conn.sql(f"SELECT * FROM '{(datadir / filename).with_suffix('.csv')}'")

    return _duck_relation
