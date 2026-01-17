.PHONY: help install install-dev test lint format clean run

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run linters (ruff, mypy)"
	@echo "  make format       - Format code with black and ruff"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Run the API server"
	@echo "  make setup        - Initial project setup"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

setup:
	@echo "Setting up project..."
	cp .env.example .env
	mkdir -p data/documents data/embeddings data/checkpoints data/logs
	touch data/documents/.gitkeep data/embeddings/.gitkeep data/checkpoints/.gitkeep data/logs/.gitkeep
	@echo "Setup complete! Edit .env file with your configuration."
