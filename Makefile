.PHONY: build run stop restart logs seed seed-docker test test-docker test-cov test-cov-docker docs docs-docker clean

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
	python -m pytest

test-docker:    ## Run pytest suite inside the web container
	docker compose exec -T web python -m pytest

test-cov:       ## Run pytest suite with coverage report
	python -m pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=75

test-cov-docker: ## Run pytest suite with coverage report inside the web container
	docker compose exec -T web python -m pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=75

docs:           ## Build Sphinx documentation
	python -m sphinx -b html docs docs/_build/html

docs-docker:    ## Build Sphinx documentation inside the web container
	docker compose exec -T web sphinx-build -b html docs docs/_build/html

clean:          ## Stop and remove containers, images, volumes, networks
	docker compose down --volumes --rmi local
	docker container prune -f
	docker image prune -a -f
	docker volume prune -f
	docker network prune -f
