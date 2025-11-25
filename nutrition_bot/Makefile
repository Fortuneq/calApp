.PHONY: help install run test docker-build docker-up docker-down logs clean

help:
	@echo "Nutrition Bot - Makefile Commands"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run bot locally"
	@echo "  make test          - Run tests"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make logs          - View Docker logs"
	@echo "  make clean         - Clean cache files"

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest tests/ -v

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f bot

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
