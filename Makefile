export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

watch:
	git ls-files | entr pytest tests/unit
