#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing package in editable mode..."
pip install -e .

echo "Running tests..."
pytest --maxfail=1 --disable-warnings -q

echo "✅ All checks passed" 