#!/bin/bash
set -e

source venv/bin/activate

echo "Running ruff check..."
ruff check src/ tests/

echo "Running pytest..."
pytest -q

echo "Removing old dist directory..."
rm -rf dist

echo "Building wheel..."
python -m build

echo "Uploading to PyPI..."
python -m twine upload dist/*
