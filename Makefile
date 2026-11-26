# Variables
PYTHON = python3
UV = uv
PYTEST = coverage run -m pytest
TEST_REPORT = coverage report -m
MYPY = mypy
RUFF = ruff
CHECKFILES = pyttings/ tests/
PYTHON_VERSIONS ?= 3.11 3.12 3.13 3.14

UV_INSTALLED := $(shell command -v $(UV) 2> /dev/null)

# Default target
all: test

# Install uv if not found
install-uv:
ifndef UV_INSTALLED
	@echo "uv is not installed. Would you like to install it? (y/n)"
	@read -p "Choice: " choice; \
	if [ "$$choice" = "y" ]; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "uv installed successfully."; \
	else \
		echo "uv is required. Exiting."; \
		exit 1; \
	fi
endif

# Set up the environment and install dependencies
setup: install-uv
	$(UV) sync --all-extras --dev

# Run tests on the current Python environment (pytest and mypy)
test-current: setup
	$(UV) run $(PYTEST) $(CHECKFILES) -s
	$(UV) run $(TEST_REPORT)
	$(UV) run $(MYPY) $(CHECKFILES)
	$(UV) run $(RUFF) format --diff $(CHECKFILES)
	$(UV) run $(RUFF) check --select I $(CHECKFILES)

# Run pytest on every supported Python version
test-versions:
	@for version in $(PYTHON_VERSIONS); do \
		echo "Testing with Python $$version"; \
		PYTHONPATH=. $(UV) run --python $$version --no-project --with pytest \
			python -m pytest $(CHECKFILES) -q || exit 1; \
	done

# Run tests on the current environment and all supported Python versions
test: test-current test-versions

# Format and lint code (ruff)
style: setup
	$(UV) run $(RUFF) format $(CHECKFILES)
	$(UV) run $(RUFF) check --select I --fix $(CHECKFILES)

# Help message
help:
	@echo "Available targets:"
	@echo "  setup         - Set up the environment and install dependencies using uv"
	@echo "  test          - Run tests on the current environment and all supported versions"
	@echo "  test-current  - Run tests with pytest and mypy on the current environment"
	@echo "  test-versions - Run pytest on Python $(PYTHON_VERSIONS)"
	@echo "  style         - Format and lint code with ruff"
	@echo "  help          - Show this help message"