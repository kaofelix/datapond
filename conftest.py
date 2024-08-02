import shutil

import pytest


@pytest.fixture
def datadir(tmp_path, request):
    shutil.copytree(request.config.rootdir / "data", tmp_path / "data")
    return tmp_path / "data"
