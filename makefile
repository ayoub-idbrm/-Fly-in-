.PHONY: install run debug clean lint

PYTHON = uv run python
MAIN = src

install:
	uv sync

run:
	$(PYTHON) $(MAIN)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache src/.mypy_cache .pytest_cache .ruff_cache /tmp/.mypy_cache

lint:
	uv run flake8 src
	PYTHONPATH=src uv run mypy src --cache-dir=/tmp/.mypy_cache --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs