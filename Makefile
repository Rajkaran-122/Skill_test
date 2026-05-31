# ============================================================
# Store Intelligence Platform — Makefile
# ============================================================

.PHONY: help up down build logs test seed clean dev prod

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Docker Compose ----

up: ## Start all services (development)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down: ## Stop all services
	docker compose down

build: ## Build all service images
	docker compose build

rebuild: ## Rebuild all service images (no cache)
	docker compose build --no-cache

logs: ## Tail logs for all services
	docker compose logs -f

logs-api: ## Tail API service logs
	docker compose logs -f api

logs-cv: ## Tail CV pipeline logs
	docker compose logs -f cv-pipeline

logs-processor: ## Tail event processor logs
	docker compose logs -f event-processor

prod: ## Start all services (production)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

status: ## Show service status
	docker compose ps

# ---- Development ----

dev-api: ## Run API locally (hot reload)
	cd services/api && uvicorn src.main:app --reload --port 8000

dev-dashboard: ## Run dashboard locally (hot reload)
	cd services/dashboard && npm run dev

dev-cv: ## Run CV pipeline locally
	cd services/cv-pipeline && python -m src.main

dev-processor: ## Run event processor locally
	cd services/event-processor && python -m src.main

# ---- Database ----

db-init: ## Initialize database schema
	docker compose exec postgres psql -U sip_user -d sip_db -f /docker-entrypoint-initdb.d/init.sql

db-seed: ## Seed database with sample data
	docker compose exec postgres psql -U sip_user -d sip_db -f /docker-entrypoint-initdb.d/seed.sql

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U sip_user -d sip_db

db-migrate: ## Run Alembic migrations
	cd services/api && alembic upgrade head

# ---- Kafka ----

kafka-topics: ## Create Kafka topics
	docker compose exec kafka bash /opt/kafka/create-topics.sh

kafka-shell: ## Open Kafka shell
	docker compose exec kafka bash

# ---- Redis ----

redis-shell: ## Open Redis CLI
	docker compose exec redis redis-cli

# ---- Testing ----

test: ## Run all tests
	@echo "Running CV Pipeline tests..."
	cd services/cv-pipeline && python -m pytest tests/ -v
	@echo "Running Event Processor tests..."
	cd services/event-processor && python -m pytest tests/ -v
	@echo "Running API tests..."
	cd services/api && python -m pytest tests/ -v
	@echo "Running Dashboard tests..."
	cd services/dashboard && npm test

test-cv: ## Run CV pipeline tests
	cd services/cv-pipeline && python -m pytest tests/ -v --cov=src --cov-report=term-missing

test-processor: ## Run event processor tests
	cd services/event-processor && python -m pytest tests/ -v --cov=src --cov-report=term-missing

test-api: ## Run API tests
	cd services/api && python -m pytest tests/ -v --cov=src --cov-report=term-missing

test-dashboard: ## Run dashboard tests
	cd services/dashboard && npm test

test-e2e: ## Run end-to-end tests
	python scripts/simulate_video.py --events 1000 && sleep 5 && cd services/api && python -m pytest tests/integration/ -v

# ---- Simulation ----

simulate: ## Run event simulation (1000 events)
	python scripts/simulate_video.py --events 1000

load-test: ## Run load test (10k events/sec)
	locust -f scripts/load_test.py --headless -u 100 -r 10 -t 60s

# ---- Cleanup ----

clean: ## Remove all containers, volumes, and images
	docker compose down -v --rmi all --remove-orphans

clean-volumes: ## Remove data volumes only
	docker compose down -v

prune: ## Docker system prune
	docker system prune -af --volumes
