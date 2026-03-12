#!/bin/bash
# Run all tests with coverage

set -e

echo "Running unit tests..."
pytest tests/unit/ -v --cov=lambdax --cov-report=term

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v --cov=lambdax --cov-append --cov-report=term

echo ""
echo "Generating coverage report..."
pytest --cov=lambdax --cov-report=html --cov-report=term-missing

echo ""
echo "Coverage report generated in htmlcov/index.html"
