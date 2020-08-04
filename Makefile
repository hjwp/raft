export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
SHELL = zsh

watch:
	ls **/*.py | entr pytest tests/unit

pylint:  ## runs just pylint
	pylint -j0 src tests

black:  ## run just black
	black -l 99 src tests --check --exclude migrations/*

mypy: ## run just mypy
	dmypy run src tests/*

lint: pylint black mypy  ## run all linters locally

pretty:  ## make the code pretty
	black -l 99 src tests

unit:  ## run unit tests
	pytest tests/unit

integration:  ## run integration tests
	pytest tests/integration

all: unit integration lint
