# RouteAI Enterprise Backend Foundation

RouteAI is an enterprise-grade AI-Powered Logistics Route Optimization Platform. This repository contains the asynchronous Python backend foundation built using FastAPI, SQLAlchemy 2.0, Pydantic v2, and Alembic.

## Technology Stack

- **Framework**: FastAPI (Async Python 3.10+)
- **ORM**: SQLAlchemy 2.0 (Async Engine & async_sessionmaker)
- **Database Migrations**: Alembic
- **Database**: Supabase PostgreSQL / PostgreSQL (asyncpg driver)
- **Settings Management**: Pydantic-Settings v2
- **Authentication & Security**: PyJWT (HS256) & Passlib / Bcrypt password hashing
- **Deployment Target**: Render / Cloud Containers

## Project Structure

```
backend/
├── alembic/              # Database migration scripts & env.py
├── app/
│   ├── api/              # API routes & Dependency Injection
│   ├── core/             # Application configuration, DB, logging, security, exceptions
│   ├── db/               # Database initialization & Alembic metadata registry
│   ├── middleware/       # Custom ASGI middlewares (Request ID, Timing)
│   ├── models/           # SQLAlchemy 2.0 Base model & domain entities
│   ├── repositories/     # Generic Async Repository pattern implementation
│   ├── schemas/          # Pydantic v2 Base schemas & API response contracts
│   ├── services/         # Generic Business Service layer
│   └── main.py           # Application entrypoint & lifespan handling
├── .env.example          # Environment variable template
├── .env                  # Local environment file
├── alembic.ini           # Alembic configuration file
├── pyproject.toml        # Project metadata & tools config
└── requirements.txt      # Dependency specification
```

## Setup & Local Execution

1. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Verify Health Endpoint**:
   Visit `http://127.0.0.1:8000/api/v1/health` or view Swagger UI docs at `http://127.0.0.1:8000/docs`.
