#!/bin/bash
# Coverage check script for local development
# Usage: ./check_coverage.sh [--report] [--html]

set -e

PYTHON_CMD="python3.12"
FAIL_UNDER=85

echo "🧪 Running unit tests with coverage..."
echo ""

# Build pytest command
PYTEST_CMD="$PYTHON_CMD -m pytest tests/unit \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --cov-fail-under=$FAIL_UNDER \
  -v"

# Optional: Generate HTML report
if [[ "$1" == "--html" || "$2" == "--html" ]]; then
  PYTEST_CMD="$PYTEST_CMD --cov-report=html:htmlcov"
fi

# Run tests
if eval $PYTEST_CMD; then
  echo ""
  echo "✅ Coverage gate PASSED (>= $FAIL_UNDER%)"
  
  if [[ "$1" == "--html" || "$2" == "--html" ]]; then
    echo "📊 HTML report generated: htmlcov/index.html"
  fi
  
  exit 0
else
  echo ""
  echo "❌ Coverage gate FAILED (< $FAIL_UNDER%)"
  echo "📊 See htmlcov/index.html for detailed report"
  exit 1
fi
