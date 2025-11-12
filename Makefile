.PHONY: install build test lint clean docker-build docker-run

# Python installation
install-python:
	pip install -e .

# Node.js installation
install-node:
	npm install

# Build Python package
build-python:
	python -m build

# Build TypeScript
build-ts:
	npm run build

# Run tests
test:
	pytest tests/
	npm test

# Lint code
lint:
	flake8 src/python/
	npm run lint

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/ lib/ node_modules/
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# Docker build
docker-build:
	docker build -t azw3/pipeline:latest .

# Docker run
docker-run:
	docker-compose up -d

# Install all dependencies
install: install-python install-node

# Build all
build: build-python build-ts

