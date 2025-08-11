# OHDSI WebAPI Client - Development Makefile
# Run these commands locally before pushing to save CI time

.PHONY: help lint format typecheck test test-unit test-integration test-live test-all ci-check build clean install

# Default target
help:
	@echo "OHDSI WebAPI Client - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Quick checks (run these before pushing):"
	@echo "  make ci-check     - Run all CI checks locally"
	@echo "  make test         - Run unit + integration tests"
	@echo "  make lint         - Check code style and imports"
	@echo "  make format       - Format code with black"
	@echo "  make typecheck    - Run mypy type checking"
	@echo ""
	@echo "Individual commands:"
	@echo "  make fix          - Fix auto-fixable linting issues"
	@echo "  make fix-unsafe   - Fix auto-fixable issues + type modernization"
	@echo "  make test-unit    - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-live    - Run tests against live API (requires .env)"
	@echo "  make test-all     - Run all tests including live"
	@echo "  make build        - Build package for distribution"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make install      - Install/reinstall development dependencies"

# Main CI check - runs the same checks as GitHub Actions
# Note: typecheck commented out until type annotations are cleaned up
ci-check: lint test build
	@echo ""
	@echo "✅ All CI checks passed! Ready to push to GitHub."
	@echo "💡 Optional: Run 'make typecheck' to check types"
	@echo "💡 Optional: Run 'make test-live' to test against real API"

# Linting and formatting
lint:
	@echo "🔍 Checking code style with ruff..."
	poetry run ruff check .
	@echo "🔍 Checking code formatting with black..."
	poetry run black --check .

fix:
	@echo "🔧 Fixing auto-fixable issues with ruff..."
	poetry run ruff check . --fix
	@echo "🔧 Formatting code with black..."
	poetry run black .

fix-unsafe:
	@echo "🔧 Fixing auto-fixable issues with ruff (including unsafe fixes)..."
	poetry run ruff check . --fix --unsafe-fixes
	@echo "🔧 Formatting code with black..."
	poetry run black .

format:
	@echo "🎨 Formatting code with black..."
	poetry run black .

# Type checking
typecheck:
	@echo "🔍 Type checking with mypy..."
	poetry run mypy src/

# Testing
test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	poetry run pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	poetry run pytest tests/integration/ -v

test-live:
	@echo "🌐 Running live API tests (requires .env with valid credentials)..."
	poetry run pytest tests/live/ -v

test-all: test-unit test-integration test-live

# Package management
build:
	@echo "📦 Building package..."
	poetry build

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	@echo "📥 Installing development dependencies..."
	poetry install

# Coverage report
coverage:
	@echo "📊 Running tests with coverage..."
	poetry run pytest tests/unit/ tests/integration/ --cov=ohdsi_webapi --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"
