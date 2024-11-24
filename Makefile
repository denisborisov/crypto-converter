include .env
export
export PYTEST_COVER_PERCENT=80
export PYTHONDONTWRITEBYTECODE=1

.PHONY: test
test:
    # Run tests related to the Crypto Converter app.
	poetry run pytest --cov-fail-under=${PYTEST_COVER_PERCENT} \
						tests/

.PHONY: up
up:
    # Run the Crypto Converter app.
	if [ ! -f .env ]; then \
		echo ".env file not found!"; \
		exit 1; \
	fi
	docker compose up --build

.PHONY: down
down:
	docker-compose down --remove-orphans \
                        --volumes

.PHONY: cleanup
cleanup:
	docker rm $(docker ps -aq)
	docker rmi $(docker image ls -q)
