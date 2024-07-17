SYSTEM_PYTHON := python3
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV_PATH := $(MAKEFILE_DIR).venv

.venv:
	$(SYSTEM_PYTHON) -m venv --upgrade-deps --prompt . .venv
	$(VENV_PATH)/bin/pip install uv

requirements.lock: .venv pyproject.toml
	$(VENV_PATH)/bin/uv pip compile -o requirements.lock pyproject.toml

requirements-dev.lock: .venv pyproject.toml
	$(VENV_PATH)/bin/uv pip compile --extra dev -o requirements-dev.lock pyproject.toml

.PHONY: sync
sync: requirements.lock requirements-dev.lock
	$(VENV_PATH)/bin/uv pip sync requirements.lock requirements-dev.lock
