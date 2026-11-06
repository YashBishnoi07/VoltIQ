.PHONY: setup train api web test clean docker-up docker-down

setup:
	python -m pip install -e ".[dev]"
	cd frontend && npm install

train:
	python scripts/train.py

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

web:
	cd frontend && npm run dev

test:
	pytest tests/ -v

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	rm -rf data/interim/* data/processed/* models_store/* frontend/dist
