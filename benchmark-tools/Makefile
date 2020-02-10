#!/usr/bin/make -f

VENV_NAME ?= venv
VENV_ACTIVATE := . $(VENV_NAME)/bin/activate
PYTHON := ${VENV_NAME}/bin/python3

default: setup test lint
.PHONY: default

mock-run: setup
	${PYTHON} perf.py run --mock .
.PHONY: mock

setup:
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	touch $(VENV_ACTIVATE)
.PHONY: setup

test:
	${PYTHON} -m pytest
.PHONY: test

lint:
	${PYTHON} -m pylint harness/ benchmarks/ perf.py
.PHONY: lint

clean:
	@find . -name \*.pyc -o -name __pycache__ -exec rm -rf {} \; 2>/dev/null || true
	@rm -rf ${VENV_NAME}
.PHONY: clean
