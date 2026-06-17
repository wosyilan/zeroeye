.PHONY: test test-cov test-live clean

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=tests --cov-report=term

test-live:
	pytest tests/ --live

clean:
	rm -rf .pytest_cache .coverage __pycache__ tests/__pycache__ tests/data/__pycache__
