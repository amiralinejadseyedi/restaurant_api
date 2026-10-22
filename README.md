# Restaurant API

A RESTful API for managing restaurant orders, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Create, retrieve, update, and delete restaurant orders
- Validate request data using Pydantic
- Handle database errors with appropriate HTTP status codes
- Manage database schema changes using Alembic
- Run the API and PostgreSQL using Docker Compose
- Test API endpoints using Pytest

## Tech Stack

- Python 3.14
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL 17
- Psycopg
- Alembic
- Docker and Docker Compose
- Pytest

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check API status |
| POST | `/orders` | Create an order |
| GET | `/orders` | Retrieve all orders |
| PUT | `/orders/{order_id}` | Update an order |
| DELETE | `/orders/{order_id}` | Delete an order |

## Order Fields and Validation

| Field | Type | Validation |
|---|---|---|
| `customer_name` | String | 1–100 characters; cannot contain only spaces |
| `food_name` | String | 1–100 characters; cannot contain only spaces |
| `quantity` | Integer | Greater than zero |
| `price` | Number | Greater than zero |

## Error Handling

The API returns appropriate HTTP status codes:

- `201 Created` — Order created successfully
- `404 Not Found` — Requested order does not exist
- `422 Unprocessable Entity` — Request validation failed
- `500 Internal Server Error` — Database operation failed

## Prerequisites

- Docker Desktop
- Docker Compose

## Configuration

Create a `.env` file in the project root containing the database environment variables expected by `compose.yaml`:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

Use your own credentials. Do not commit `.env` or real database passwords to GitHub.

The Compose configuration also uses an external Docker volume named `restaurant-data`. If it does not already exist, create it before starting the application:

```bash
docker volume create restaurant-data
```

## Run the Application

Build and start the services from the project root:

```bash
docker compose up -d --build
```

Check the service status:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs api
```

View database logs:

```bash
docker compose logs db
```

## Database Migrations

Apply the existing Alembic migrations after the API container is running:

```bash
docker compose exec api alembic upgrade head
```

The migration configuration reads `DATABASE_URL` from the environment, allowing Alembic to connect to the configured PostgreSQL database.

## API Documentation

When the API is running, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Run Tests

Install Pytest in your development environment if it is not already installed:

```bash
python -m pip install pytest
```

Run the automated tests:

```bash
python -m pytest -v
```

The API tests use an isolated SQLite database to avoid modifying the PostgreSQL database used by the running application.

## Stop the Application

```bash
docker compose down
```

This command stops and removes the Compose containers and network. Named volumes are retained unless explicitly removed.

## Future Improvements

- Add authentication and authorization
- Add pagination and filtering
- Expand automated test coverage
- Add continuous integration
- Deploy the API to a production environment

## Author

Amir Alinezhad Seyedi

GitHub: [amiralinejadseyedi](https://github.com/amiralinejadseyedi)
