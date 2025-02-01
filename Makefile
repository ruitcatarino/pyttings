# Variables
PYTHON = python3
UV = uv
PYTEST = pytest
MYPY = mypy
RUFF = ruff
CHECKFILES = pyttings/ tests/

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
	$(UV) sync

# Run tests (pytest and mypy)
test: setup
	$(UV) run $(PYTEST) $(CHECKFILES)
	$(UV) run $(MYPY) $(CHECKFILES)

# Format and lint code (ruff)
style: setup
	$(UV) run $(RUFF) format $(CHECKFILES)
	$(UV) run $(RUFF) check --select I --fix $(CHECKFILES)

# Help message
help:
	@echo "Available targets:"
	@echo "  setup       - Set up the environment and install dependencies using uv"
	@echo "  test        - Run tests with pytest and mypy"
	@echo "  style       - Format and lint code with ruff"
	@echo "  help        - Show this help message"