.DEFAULT_GOAL :=all
run:
	docker-compose up --build
all: run