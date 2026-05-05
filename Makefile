SHELL 		:= /bin/bash
UV 			:= uv
VENV_DIR 	:= .venv

.PHONY: install install-dev format lint test pre-commit-install pre-commit-run docs-init docs-update tf-fmt tf-validate clean

install:
	$(UV) sync --all-packages

install-dev:
	$(UV) sync --all-packages --all-extras

format:
	$(UV) run ruff format packages/ tests/
	terraform -chdir=terraform fmt -recursive

lint:
	$(UV) run ruff format --check packages/ tests/
	$(UV) run ruff check packages/ tests/
	terraform -chdir=terraform fmt -check -recursive

test:
	$(UV) run pytest tests/

pre-commit-install:
	$(UV) run pre-commit install

pre-commit-run:
	$(UV) run pre-commit run --all-files

docs-init:
	git submodule update --init --recursive

docs-update:
	git submodule update --remote --merge

tf-fmt:
	terraform -chdir=terraform fmt -recursive

tf-validate:
	cd terraform && terraform init -backend=false && terraform validate

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf .venv coverage/ dist/ build/ *.egg-info
