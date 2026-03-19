---
name: fastapi-endpoint-patterns
description: Conventions for writing FastAPI endpoints with proper typing, status codes, and error handling
license: Apache-2.0
---

# Endpoint Patterns

## Basic Endpoint Structure

Always use `async def`. Specify `response_model` and `status_code`.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.services import user_service

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await user_service.create_user(db, payload)
    return user
```

## Response Models

Define separate schemas for create, read, and update operations:

```python
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

- `UserCreate` -- what the client sends to create a resource.
- `UserUpdate` -- partial update; all fields optional.
- `UserRead` -- what the API returns. Includes `id`, excludes `password`.

## Status Codes

Use explicit status codes from `fastapi.status`:

| Operation | Status Code | Constant |
|-----------|------------|----------|
| Create | 201 | `HTTP_201_CREATED` |
| Read | 200 | `HTTP_200_OK` (default) |
| Update | 200 | `HTTP_200_OK` |
| Delete | 204 | `HTTP_204_NO_CONTENT` |

For 204 responses, set `response_model=None`:

```python
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    await user_service.delete_user(db, user_id)
```

## Dependency Injection

Inject shared resources with `Depends()`:

```python
from fastapi import Depends
from app.deps.auth import get_current_user
from app.deps.database import get_db

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    return current_user
```

Chain dependencies for layered auth:

```python
# app/deps/auth.py
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def require_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user
```

## Error Handling

Raise `HTTPException` for expected errors:

```python
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user
```

Use exception handlers for global error formatting:

```python
# app/main.py
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

## Path and Query Parameters

```python
@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    return await user_service.list_users(db, skip=skip, limit=limit, search=search)
```

Use `Path()` and `Query()` for validation:

```python
from fastapi import Path, Query

@router.get("/{user_id}")
async def get_user(
    user_id: int = Path(..., gt=0, description="The user ID"),
    fields: list[str] = Query(default=[], description="Fields to include"),
):
    ...
```
