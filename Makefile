.DEFAULT_GOAL := help
.PHONY: help install install-dev lint lint-fix format format-md typecheck quality test test-parallel test-migrate test-teardown docs-serve docs-build docs-clean build clean all dev

# Colors for output
YELLOW := \033[33m
GREEN := \033[32m
BLUE := \033[34m
RED := \033[31m
RESET := \033[0m

# Project variables
PYTHON := python3
UV := uv
PYTEST := pytest
RUFF := ruff
STYLUA := stylua
TYPECHECK := basedpyright
MKDOCS := mkdocs
MDFORMAT := mdformat
BALATRO_SCRIPT := ./balatro.sh

# Test ports for parallel testing
TEST_PORTS := 12346 12347 12348 12349

help: ## Show this help message
	@echo "$(BLUE)BalatroBot Development Makefile$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install package dependencies
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	$(UV) sync

install-dev: ## Install package with development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(RESET)"
	$(UV) sync --all-extras

# Code quality targets
lint: ## Run ruff linter (check only)
	@echo "$(YELLOW)Running ruff linter...$(RESET)"
	$(RUFF) check --select I .
	$(RUFF) check .

lint-fix: ## Run ruff linter with auto-fixes
	@echo "$(YELLOW)Running ruff linter with fixes...$(RESET)"
	$(RUFF) check --select I --fix .
	$(RUFF) check --fix .

format: ## Run ruff formatter
	@echo "$(YELLOW)Running ruff formatter...$(RESET)"
	$(RUFF) check --select I --fix .
	$(RUFF) format .
	@echo "$(YELLOW)Running stylua formatter...$(RESET)"
	$(STYLUA) src/lua

format-md: ## Run markdown formatter
	@echo "$(YELLOW)Running markdown formatter...$(RESET)"
	$(MDFORMAT) .

typecheck: ## Run type checker
	@echo "$(YELLOW)Running type checker...$(RESET)"
	$(TYPECHECK)

quality: lint format typecheck ## Run all code quality checks
	@echo "$(GREEN) All quality checks completed$(RESET)"

# Testing targets
test: ## Run tests with single Balatro instance (auto-starts if needed)
	@echo "$(YELLOW)Running tests...$(RESET)"
	@if ! $(BALATRO_SCRIPT) --status | grep -q "12346"; then \
		echo "Starting Balatro on port 12346..."; \
		$(BALATRO_SCRIPT) --headless --fast -p 12346; \
		sleep 1; \
	fi
	$(PYTEST)

test-parallel: ## Run tests in parallel on 4 instances (auto-starts if needed)
	@echo "$(YELLOW)Running parallel tests...$(RESET)"
	@running_count=$$($(BALATRO_SCRIPT) --status | grep -E "($(word 1,$(TEST_PORTS))|$(word 2,$(TEST_PORTS))|$(word 3,$(TEST_PORTS))|$(word 4,$(TEST_PORTS)))" | wc -l); \
	if [ "$$running_count" -ne 4 ]; then \
		echo "Starting Balatro instances on ports: $(TEST_PORTS)"; \
		$(BALATRO_SCRIPT) --headless --fast -p $(word 1,$(TEST_PORTS)) -p $(word 2,$(TEST_PORTS)) -p $(word 3,$(TEST_PORTS)) -p $(word 4,$(TEST_PORTS)); \
		sleep 1; \
	fi
	$(PYTEST) -n 4 --port $(word 1,$(TEST_PORTS)) --port $(word 2,$(TEST_PORTS)) --port $(word 3,$(TEST_PORTS)) --port $(word 4,$(TEST_PORTS)) tests/lua/

test-migrate: ## Run replay.py on all JSONL files in tests/runs/ using 4 parallel instances
	@echo "$(YELLOW)Running replay migration on tests/runs/ files...$(RESET)"
	@running_count=$$($(BALATRO_SCRIPT) --status | grep -E "($(word 1,$(TEST_PORTS))|$(word 2,$(TEST_PORTS))|$(word 3,$(TEST_PORTS))|$(word 4,$(TEST_PORTS)))" | wc -l); \
	if [ "$$running_count" -ne 4 ]; then \
		echo "Starting Balatro instances on ports: $(TEST_PORTS)"; \
		$(BALATRO_SCRIPT) --headless --fast -p $(word 1,$(TEST_PORTS)) -p $(word 2,$(TEST_PORTS)) -p $(word 3,$(TEST_PORTS)) -p $(word 4,$(TEST_PORTS)); \
		sleep 1; \
	fi
	@jsonl_files=$$(find tests/runs -name "*.jsonl" -not -name "*.skip" | sort); \
	if [ -z "$$jsonl_files" ]; then \
		echo "$(RED)No .jsonl files found in tests/runs/$(RESET)"; \
		exit 1; \
	fi; \
	file_count=$$(echo "$$jsonl_files" | wc -l); \
	echo "Found $$file_count .jsonl files to process"; \
	ports=($(TEST_PORTS)); \
	port_idx=0; \
	for file in $$jsonl_files; do \
		port=$${ports[$$port_idx]}; \
		echo "Processing $$file on port $$port..."; \
		$(PYTHON) bots/replay.py --input "$$file" --port $$port & \
		port_idx=$$((port_idx + 1)); \
		if [ $$port_idx -eq 4 ]; then \
			port_idx=0; \
		fi; \
	done; \
	wait; \
	echo "$(GREEN)✓ All replay migrations completed$(RESET)"

test-teardown: ## Kill all Balatro instances
	@echo "$(YELLOW)Killing all Balatro instances...$(RESET)"
	$(BALATRO_SCRIPT) --kill
	@echo "$(GREEN) All instances stopped$(RESET)"

# Documentation targets
docs-serve: ## Serve documentation locally
	@echo "$(YELLOW)Starting documentation server...$(RESET)"
	$(MKDOCS) serve

docs-build: ## Build documentation
	@echo "$(YELLOW)Building documentation...$(RESET)"
	$(MKDOCS) build

docs-clean: ## Clean built documentation
	@echo "$(YELLOW)Cleaning documentation build...$(RESET)"
	rm -rf site/

# Build targets
build: ## Build package for distribution
	@echo "$(YELLOW)Building package...$(RESET)"
	$(PYTHON) -m build

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/ coverage.xml
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN) Cleanup completed$(RESET)"

# Convenience targets
dev: format lint typecheck ## Quick development check (no tests)
	@echo "$(GREEN) Development checks completed$(RESET)"

all: format lint typecheck test ## Complete quality check with tests
	@echo "$(GREEN) All checks completed successfully$(RESET)"
