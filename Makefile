# Makefile

define HELP_MESSAGE
                    Discord Bot
                    -----------

Welcome to the discord bot package!

# Installing

1. Create a new Conda environment: `conda create --name discord-bot python=3.11`
2. Activate the environment: `conda activate discord-bot`
3. Install the package: `make install-dev`

# Running Tests

1. Run autoformatting: `make format`
2. Run static checks: `make static-checks`
3. Run unit tests: `make test`

endef
export HELP_MESSAGE

all:
	@echo "$$HELP_MESSAGE"
.PHONY: all

# ------------------------ #
#      Development         #
# ------------------------ #

env_file := .env.local
# env_file := .env.dev
# env_file := .env.prod

start-backend:
	DPSH_ENVIRONMENT_SECRETS=$(env_file) uvicorn bot.api.app.main:app --reload --port 8000 --host localhost --env-file $(env_file)

start-frontend:
	cd frontend && npm start

start-worker:
	DPSH_ENVIRONMENT_SECRETS=$(env_file) PYTORCH_ENABLE_MPS_FALLBACK=1 python -m bot.worker.server --debug

# ------------------------ #
#          DB              #
# ------------------------ #

create-db:
	DPSH_ENVIRONMENT_SECRETS=.env.dev python -m bot.api.db

aerich-init:
	DPSH_ENVIRONMENT_SECRETS=.env.dev aerich init --tortoise-orm bot.api.db.CONFIG --location bot/api/migrations/

aerich-init-db:
	DPSH_ENVIRONMENT_SECRETS=.env.dev aerich init-db

aerich-migrate:
	DPSH_ENVIRONMENT_SECRETS=.env.dev aerich migrate

# ------------------------ #
#          Build           #
# ------------------------ #

install-torch-nightly:
	@pip install --pre torch --index-url https://download.pytorch.org/whl/nightly
.PHONY: install-torch-nightly

install:
	@pip install --verbose -e '.[api,worker]'
.PHONY: install

install-dev:
	@pip install --verbose -e '.[dev]'
.PHONY: install

clean:
	rm -rf build dist *.so **/*.so **/*.pyi **/*.pyc **/*.pyd **/*.pyo **/__pycache__ *.egg-info .eggs/ .ruff_cache/
.PHONY: clean

# ------------------------ #
#       Static Checks      #
# ------------------------ #

# py-files := $(shell git ls-files '*.py')

format:
	@black .
	@ruff --fix .
	@cd frontend && npm run format
.PHONY: format

static-checks:
	@black --diff --check .
	@ruff .
	@mypy --install-types --non-interactive .
.PHONY: lint

# ------------------------ #
#        Unit tests        #
# ------------------------ #

test:
	python -m pytest
.PHONY: test
