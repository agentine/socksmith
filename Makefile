.PHONY: install build test lint fmt typecheck clean ci

install:
	pip install -e ".[dev]"

build:
	python -m build

test:
	pytest --cov=socksmith --cov-report=term-missing -v

lint:
	ruff check .

fmt:
	ruff format .

typecheck:
	mypy socksmith socks.py

clean:
	rm -rf dist/ build/ *.egg-info/ .mypy_cache/ .pytest_cache/ .ruff_cache/ htmlcov/ .coverage

ci: lint typecheck test
