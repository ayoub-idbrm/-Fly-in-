INSTALL := uv
PYTHON := python3

FLAKE8 := flake8
MYPY := mypy

SRC := src

.PHONY: help install run debug test lint lint-strict clean

help:
	@echo "Available commands:"
	@echo "  make install"
	@echo "  make run"
	@echo "  make debug"
	@echo "  make test"
	@echo "  make lint"
	@echo "  make lint-strict"
	@echo "  make clean"

install:
	$(INSTALL) sync

run:
	$(PYTHON) -m src.main

debug:
	$(PYTHON) -m pdb -m src.main

test:
	$(PYTHON) -m pytest

lint:
	$(FLAKE8) $(SRC)
	$(MYPY) $(SRC)

lint-strict:
	$(FLAKE8) $(SRC)
	$(MYPY) --strict $(SRC)

clean:
	find . -type d \( \
		-name "__pycache__" -o \
		-name ".mypy_cache" -o \
		-name ".pytest_cache" \
	\) -exec rm -rf {} \;