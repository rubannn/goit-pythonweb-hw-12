.PHONY: build run stop restart logs seed seed-docker test test-cov docs clean

IMAGE_NAME = goit-fast-api
CONTAINER_NAME = app-fast-api

build:          ## Build, start containers in background, and seed test data
	docker compose up -d --build
	docker compose exec -T web python -m src.database.seed

run:            ## Run containers in foreground
	docker compose up

stop:           ## Stop containers
	docker compose down

restart:        ## Restart containers
	docker compose restart

logs:           ## Show container logs
	docker compose logs -f

seed:           ## Insert test contacts locally
	python -m src.database.seed

seed-docker:    ## Insert test contacts in Docker
	docker compose exec web python -m src.database.seed

test:           ## Run pytest suite
	pytest

test-cov:       ## Run pytest suite with coverage report
	pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=75

docs:           ## Build Sphinx documentation
	sphinx-build -b html docs docs/_build/html

clean:          ## Stop and remove containers, images, volumes, networks
	docker compose down --volumes --rmi local
	docker container prune -f
	docker image prune -a -f
	docker volume prune -f
	docker network prune -f
