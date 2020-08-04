export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
SHELL = zsh

watch:
	ls **/*.py | entr pytest tests/unit
