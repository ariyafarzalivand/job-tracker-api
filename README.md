# Job Tracker API

![Tests](https://github.com/ariyafarzalivand/job-tracker-api/actions/workflows/tests.yml/badge.svg)

A REST API for tracking job applications, built with Django REST Framework and PostgreSQL. Each user manages only their own applications.

## Features

- JWT authentication (login and token refresh)
- CRUD endpoints for job applications (company, position, status, date, notes)
- Per-user data isolation: users can only see and change their own applications
- Paginated list endpoint with filtering by status, text search and sorting
- Interactive API documentation with Swagger UI
- Application logging that records ids only, never personal data
- Automated tests with pytest, plus ruff lint and format checks, run on every push by GitHub Actions
- Docker setup with PostgreSQL for a one-command start

## Tech stack

Python 3.13, Django, Django REST Framework, Simple JWT, django-filter, drf-spectacular, PostgreSQL, pytest, ruff, Docker, GitHub Actions

## Getting started

Requires [Docker](https://docs.docker.com/engine/install/) with Docker Compose.

```bash
git clone https://github.com/ariyafarzalivand/job-tracker-api.git
cd job-tracker-api

# Create your local settings from the example file and set your own values.
cp .env.example .env

docker compose up --build
```

The API is now running at http://127.0.0.1:8000/ and the interactive documentation is at http://127.0.0.1:8000/api/docs/.

Create a user to log in with:

```bash
docker compose exec web python manage.py createsuperuser
```

## Configuration

Settings are read from the `.env` file. See `.env.example` for a template.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key. Use a long random value. |
| `DEBUG` | `True` for development, `False` otherwise. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL database used by Docker Compose. |
| `LOG_LEVEL` | Optional. Log level of the application, `INFO` by default. |

## Using the API

Get a token, then send it with each request:

```bash
# Log in and receive access and refresh tokens.
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-user", "password": "your-password"}'

# Create an application (replace <ACCESS_TOKEN> with the token from above).
curl -X POST http://127.0.0.1:8000/api/applications/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"company": "Example GmbH", "position": "Backend Developer", "applied_date": "2026-11-20"}'
```

### Filtering, search and sorting

The list endpoint returns 20 applications per page and supports these query parameters:

| Parameter | Example | Effect |
| --- | --- | --- |
| `status` | `?status=interview` | Only applications with this status (`applied`, `interview`, `offer`, `rejected`) |
| `search` | `?search=siemens` | Text search in company, position and notes |
| `ordering` | `?ordering=-applied_date` | Sort by `applied_date`, `company` or `created_at`. A leading `-` reverses the order. |
| `page` | `?page=2` | Next page of results |

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

pytest                  # run the tests
ruff check .            # lint
ruff format --check .   # check formatting
```

The tests use SQLite, so no database server is needed. The same checks run in GitHub Actions on every push.

## Project structure

```
applications/            Models, serializers, views and tests for job applications
config/                  Django settings and root URL configuration
Dockerfile               Image for the Django application
docker-compose.yml       Django and PostgreSQL services
requirements.txt         Packages needed to run the application
requirements-dev.txt     Extra packages for testing and code quality
pyproject.toml           ruff configuration
```