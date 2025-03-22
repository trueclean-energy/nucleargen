.PHONY: all install test clean test-unit test-integration test-workflow test-custom

PYTHON := python

all: install test

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) run_tests.py

test-unit:
	$(PYTHON) -m pytest tests/test_schema.py tests/test_db.py -v

test-integration:
	$(PYTHON) -m pytest tests/test_converter.py tests/test_saphire_parser.py -v

test-workflow:
	$(PYTHON) -m pytest tests/test_saphire_extraction.py tests/test_end_to_end.py -v

test-custom:
	@echo "Usage: make test-custom ZIP=/path/to/your/saphire.zip"
	@if [ -n "$(ZIP)" ] && [ -f "$(ZIP)" ]; then \
		$(PYTHON) tests/test_end_to_end.py $(ZIP); \
	else \
		echo "Error: ZIP file not provided or not found. Please specify with ZIP=/path/to/your/saphire.zip"; \
		exit 1; \
	fi

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

lint:
	$(PYTHON) -m flake8 vyom tests

build:
	$(PYTHON) -m build

publish:
	$(PYTHON) -m twine upload dist/* 