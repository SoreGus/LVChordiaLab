-include .env

PYTHON_BIN ?= python3
VENV ?= .venv

BIN := $(VENV)/bin
PIP := $(BIN)/pip
PY := $(BIN)/python

.PHONY: setup install run lint format check clean

setup:
	$(PYTHON_BIN) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@if [ ! -f .env ]; then cp .env.example .env; fi

install:
	$(PIP) install -e ".[dev]"

run:
	$(PY) -m lv_chordia_lab

lint:
	$(BIN)/ruff check src

format:
	$(BIN)/ruff format src
	$(BIN)/ruff check --fix src

check:
	$(BIN)/ruff check src
	$(BIN)/ruff format --check src

clean:
	rm -rf $(VENV) build dist *.egg-info
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete