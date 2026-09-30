PYTHON ?= python

.PHONY: install test index eval api smoke
install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	pytest

index:
	PYTHONPATH=src $(PYTHON) scripts/build_index.py

eval:
	PYTHONPATH=src $(PYTHON) scripts/evaluate.py

api:
	PYTHONPATH=src uvicorn iqda.api:app --host 0.0.0.0 --port 8000

smoke:
	PYTHONPATH=src $(PYTHON) scripts/smoke_test.py
