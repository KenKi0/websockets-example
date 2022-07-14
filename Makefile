VENV = .venv
PYTHON = $(VENV)/bin/python

.PHONY: install
install:
	@echo 'Installing python dependencies...'
	@poetry install
	@echo 'Installing and updating pre-commit...'
	@pre-commit install
	@pre-commit autoupdate

.phony: pip-to-global
pip-to-global:
	echo "[global]\nindex-url = https://pypi.org/simple" > .venv/pip.conf
