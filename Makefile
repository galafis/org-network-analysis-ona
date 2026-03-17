.PHONY: install dev lint type-check test data analyze run-api run-ui docker-up docker-down clean

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

lint:
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports

type-check:
	mypy src/ --ignore-missing-imports

test:
	pytest tests/ -v --tb=short

data:
	python -c "from src.data.generator import ONADataGenerator; g = ONADataGenerator(); g.save_all()"

analyze:
	python -c "from src.analysis.runner import run_full_analysis; run_full_analysis()"

run-api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	streamlit run src/dashboard/app.py --server.port 8501

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f data/raw/*.csv data/raw/*.json data/processed/*.csv data/reports/*.html
