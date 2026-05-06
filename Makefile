SHELL 		:= /bin/bash
UV 			:= uv
VENV_DIR 	:= .venv

.PHONY: help install install-dev format lint test pre-commit-install pre-commit-run docs-init docs-update tf-fmt tf-validate clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install:  ## Install the workspace (no dev deps)
	$(UV) sync --all-packages

install-dev:  ## Install the workspace with dev dependencies
	$(UV) sync --all-packages --all-extras

format:  ## Auto-format Python and Terraform files
	$(UV) run ruff format packages/ tests/ components/
	terraform -chdir=terraform fmt -recursive

lint:  ## Check Python and Terraform formatting + ruff lint
	$(UV) run ruff format --check packages/ tests/
	$(UV) run ruff check packages/ tests/
	terraform -chdir=terraform fmt -check -recursive

test:  ## Run pytest
	$(UV) run pytest tests/

pre-commit-install:  ## Install pre-commit hooks
	$(UV) run pre-commit install

pre-commit-run:  ## Run pre-commit hooks against every file in the repo
	$(UV) run pre-commit run --all-files

docs-init:  ## Init submodules and sparse-checkout terraform-provider to examples
	git submodule update --init --recursive
	cd docs/terraform-provider && \
		git sparse-checkout init --cone && \
		git sparse-checkout set examples

docs-update:  ## Pull latest commits across all submodules
	git submodule update --remote --merge

tf-fmt:  ## terraform fmt across the terraform/ directory
	terraform -chdir=terraform fmt -recursive

tf-validate:  ## terraform validate (provider init without state backend)
	cd terraform && terraform init -backend=false && terraform validate

clean:  ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf .venv coverage/ dist/ build/ *.egg-info
