.PHONY: install test lint format clean dev serve docker-build docker-run

install:
	pip install -e ".[dev]"

dev:
	bash scripts/setup_dev.sh

test:
	pytest tests/ -v --cov=lambdax

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	black --check src tests
	isort --check-only src tests
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info

serve:
	lambdax serve --reload

docker-build:
	docker build -t lambdax:latest .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/policy.yaml:/app/policy.yaml lambdax:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

pre-commit:
	pre-commit install
	pre-commit run --all-files
