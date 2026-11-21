# Job Tracker API

![Tests](https://github.com/ariyafarzalivand/job-tracker-api/actions/workflows/tests.yml/badge.svg)

A REST API for tracking job applications, built with Django REST Framework and PostgreSQL. Each user manages only their own applications.

## Features

- JWT authentication (login and token refresh)
- CRUD endpoints for job applications (company, position, status, date, notes)
- Per-user data isolation: users can only see and change their own applications
- Interactive API documentation with Swagger UI
- Automated tests with pytest, run on every push by GitHub Actions
- Docker setup with PostgreSQL for a one-command start

## Tech stack

Python 3.13, Django, Django REST Framework, Simple JWT, drf-spectacular, PostgreSQL, pytest, Docker, GitHub Actions

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

## Running the tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

The tests use SQLite, so no database server is needed.

## Project structure

```
applications/   Models, serializers, views and tests for job applications
config/         Django settings and root URL configuration
Dockerfile      Image for the Django application
docker-compose.yml   Django and PostgreSQL services
```