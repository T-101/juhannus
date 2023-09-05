.PHONY: build up

BASE_DIR = $(shell pwd)
CONTAINER_PORT := $(shell grep CONTAINER_PORT .env | cut -d '=' -f2)

build:
	@docker compose build
	@docker compose run --rm app python manage.py makemigrations
	@docker compose run --rm app python manage.py migrate
	@docker compose run --rm app python ./manage.py collectstatic --no-input

up:
	@docker compose up
