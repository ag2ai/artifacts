---
name: fastapi-project-structure
description: Standard directory layout and module organization for FastAPI applications
license: Apache-2.0
---

# FastAPI Project Structure

## Standard Layout

```
project/
  app/
    __init__.py
    main.py              # FastAPI app instance and lifespan
    config.py            # Settings via pydantic-settings
    api/
      __init__.py
      v1/
        __init__.py
        router.py        # Aggregates all v1 routers
        endpoints/
          __init__.py
          users.py
          items.py
    models/
      __init__.py
      user.py            # SQLAlchemy / ORM models
      item.py
    schemas/
      __init__.py
      user.py            # Pydantic request/response schemas
      item.py
    deps/
      __init__.py
      database.py        # DB session dependency
      auth.py            # Auth dependencies
    services/
      __init__.py
      user_service.py    # Business logic
      item_service.py
    db/
      __init__.py
      session.py         # Engine and session factory
      base.py            # Declarative base
  tests/
    __init__.py
    conftest.py
    test_users.py
    test_items.py
  alembic/               # Database migrations
    versions/
    env.py
  alembic.ini
  pyproject.toml
```

## Key Conventions

### `app/main.py` -- Application entry point

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, init connections
    yield
    # Shutdown: close connections
    await engine.dispose()

app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
```

### `app/api/v1/router.py` -- Aggregate routers

```python
from fastapi import APIRouter
from app.api.v1.endpoints import users, items

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
```

### `app/models/` vs `app/schemas/`

- **models/**: ORM models (SQLAlchemy). Represent database tables.
- **schemas/**: Pydantic models. Represent API request/response shapes.

Keep them separate. Never return an ORM model directly from an endpoint.

### `app/deps/` -- Dependency injection

Place reusable dependencies here. Common patterns:

```python
# app/deps/database.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### `app/services/` -- Business logic

Endpoints should be thin. Move logic into service functions:

```python
# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)
```

### `app/config.py` -- Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    model_config = {"env_file": ".env"}

settings = Settings()
```

## Rules

1. One router file per resource (users.py, items.py, etc.).
2. Never put business logic in endpoint functions. Use services.
3. Always version your API (`/api/v1/`, `/api/v2/`).
4. Use `Depends()` for all shared state (db sessions, auth, settings).
5. Keep Pydantic schemas and ORM models in separate directories.
