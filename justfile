default:
    just --list

# === Development ===

run *args:
    poetry run uvicorn src.main:app --reload {{args}}

test *args:
    poetry run pytest {{args}}

test-cov:
    poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

# === Code Quality ===

ruff *args:
    poetry run ruff check {{args}} src tests

format:
    poetry run ruff format src tests
    just ruff --fix

lint: format

type-check:
    poetry run mypy src

security-check:
    poetry run bandit -c pyproject.toml -r src

check-all: format type-check security-check

pre-commit:
    poetry run pre-commit run --all-files

# === Database ===

mm *args:
    poetry run alembic revision --autogenerate -m "{{args}}"

migrate:
    poetry run alembic upgrade head

downgrade *args:
    poetry run alembic downgrade {{args}}

db-reset:
    poetry run alembic downgrade base
    poetry run alembic upgrade head

# === Docker ===

up:
    docker compose up -d

down:
    docker compose down

kill *args:
    docker compose kill {{args}}

build:
    docker compose build

ps:
    docker compose ps

logs *args:
    docker compose logs -f {{args}}

# === Setup ===

install:
    poetry install
    poetry run pre-commit install
    poetry run pre-commit install --hook-type commit-msg

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf htmlcov .coverage 2>/dev/null || true
