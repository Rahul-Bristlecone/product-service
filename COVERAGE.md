# Coverage Gate & Reporting Setup

## Overview
This project enforces a **minimum code coverage threshold of 85%** in both local development and CI/CD pipelines.

## Configuration Files

### .coveragerc
- Located at project root
- Defines coverage thresholds, omissions, and report formats
- Fail threshold: 85%
- Excludes test files, migrations, and standard patterns

### pyproject.toml
- Pytest-cov configuration with coverage flags
- Automatically runs coverage on all `pytest` invocations with `--cov=src`
- Generates HTML, XML, and terminal reports

### Jenkinsfile
- **Stage: "Run Tests with Coverage"** runs pytest with coverage enforcement
- **Stage: "Archive Artifacts"** publishes HTML coverage reports to Jenkins
- Cobertura plugin integration for trend analysis (optional if plugin installed)

## Running Tests Locally with Coverage

### Quick Run (with coverage enforcement)
```bash
python3.12 -m pytest tests/unit --cov=src --cov-report=term-missing --cov-fail-under=85
```

### Generate HTML Report
```bash
python3.12 -m pytest tests/unit \
  --cov=src \
  --cov-report=html:htmlcov \
  --cov-report=term-missing
```
Then open `htmlcov/index.html` in a browser.

### Bypass Coverage Threshold (for debugging)
```bash
python3.12 -m pytest tests/unit --cov=src --cov-report=term-missing --no-cov-on-fail
```

## Coverage Report Locations

| Format | Location | Purpose |
|--------|----------|---------|
| HTML | `htmlcov/index.html` | Interactive, line-by-line view |
| XML | `coverage.xml` | CI/CD integration (Cobertura, etc.) |
| Terminal | stdout | Quick summary in console |

## Current Coverage Status

**Last Run:** 82.35% (Below threshold of 85%)

### Coverage by Module
| Module | Coverage | Status |
|--------|----------|--------|
| `src/product/__init__.py` | 100% | ✅ Complete |
| `src/product/main.py` | 100% | ✅ Complete |
| `src/product/models/` | 100% | ✅ Complete |
| `src/product/schemas/` | 100% | ✅ Complete |
| `src/product/extentions/` | 100% | ✅ Complete |
| `src/product/resources/health.py` | 100% | ✅ Complete |
| `src/product/resources/products.py` | **65.38%** | ❌ Needs tests |

### Uncovered Code in `src/product/resources/products.py`
Lines not covered (missing tests):
- **Line 77**: Full endpoint classes (GET, PUT, DELETE, LIST)
- **Lines 88-91, 97-122, 126-138, 149-150**: Endpoint handler methods

## Next Steps to Reach 85%

To achieve the 85% threshold, add integration tests for:

1. **GET /product/<product_id>** endpoint
   - Successful retrieval
   - 404 when product not found
   - Authorization failures

2. **PUT /product/<product_id>** endpoint
   - Successful update
   - Rejection of product_code updates
   - Duplicate barcode handling
   - Database errors

3. **DELETE /product/<product_id>** endpoint
   - Successful deletion
   - Authorization failures
   - Database error handling

4. **GET /products** endpoint
   - Retrieval of user's products
   - Empty list handling
   - Authorization failures

## CI/CD Pipeline Integration

### Jenkins
The Jenkinsfile automatically:
1. Runs tests with coverage (`--cov-fail-under=85`)
2. Generates HTML and XML reports
3. Archives reports as build artifacts
4. **Fails the build** if coverage drops below 85%
5. Publishes interactive coverage report in Jenkins UI

### GitHub Actions / GitLab CI
To implement in other CI systems, add:
```yaml
- name: Test with Coverage
  run: |
    pytest tests/unit \
      --cov=src \
      --cov-report=term-missing \
      --cov-report=xml \
      --cov-fail-under=85
```

## Debugging Coverage Issues

### See what lines are not covered:
```bash
python3.12 -m pytest tests/unit --cov=src --cov-report=term-missing --cov-report=html
```

### Check a specific file:
```bash
python3.12 -m pytest tests/unit --cov=src.product.resources.products --cov-report=term-missing
```

### Exclude specific patterns (in .coveragerc):
```ini
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    ...
```

## Best Practices

1. **Keep coverage above 85%** before merging pull requests
2. **Don't add `# pragma: no cover`** lightly—test instead
3. **Run coverage locally** before pushing to CI
4. **Review coverage report** as part of code review
5. **Track trends** over time to catch coverage regressions

## Resources

- [Coverage.py docs](https://coverage.readthedocs.io/)
- [Pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [Cobertura plugin for Jenkins](https://plugins.jenkins.io/cobertura/)
