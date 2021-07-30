PYTHON = python3
PYTHON_BIN = .venv/bin/
.PHONY: clean clean-build clean-pyc lint tests test-all build

.venv/bin/activate:
	$(PYTHON) -m venv .venv

venv: .venv/bin/activate
	$(PYTHON_BIN)pip install -e '.[dev]'

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

lint:
	$(PYTHON_BIN)tox -e lint

test:
	$(PYTHON_BIN)pytest tests

test-all:
	$(PYTHON_BIN)tox

tox-with-system-python:
	$(PYTHON_BIN)tox -e py

build:
	$(PYTHON_BIN)python setup.py build
	$(PYTHON_BIN)python setup.py install

dist:
	$(PYTHON_BIN)python setup.py build
	$(PYTHON_BIN)python setup.py sdist
