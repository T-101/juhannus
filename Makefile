.PHONY: build start stop up

CONTAINER_PORT := $(shell grep CONTAINER_PORT .env | cut -d '=' -f2)

build:
	@docker-compose build
	@docker-compose run juhannus python ./manage.py collectstatic --no-input
	@docker build -t juhannus .

start:
	@docker start juhannus

stop:
	@docker stop juhannus

up:
	@docker run --env-file=.env -p 127.0.0.1:${CONTAINER_PORT}:${CONTAINER_PORT} -v /opt/juhannus.suomiscene.fi/app:/juhannus/app --name juhannus -d juhannus
