---
name: add-crud-endpoint
description: Step-by-step workflow for adding a new CRUD endpoint to a FastAPI application
license: Apache-2.0
---

# Add a CRUD Endpoint

Follow these steps to add a complete CRUD resource to a FastAPI application.

## Step 1: Create the Pydantic Schemas

Create `app/schemas/<resource>.py`:

```python
from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

## Step 2: Create the ORM Model

Create `app/models/<resource>.py`:

```python
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    price: Mapped[float] = mapped_column(Float)
```

## Step 3: Create the Service Layer

Create `app/services/<resource>_service.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

async def create_item(db: AsyncSession, payload: ItemCreate) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    return await db.get(Item, item_id)

async def list_items(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Item]:
    result = await db.execute(select(Item).offset(skip).limit(limit))
    return list(result.scalars().all())

async def update_item(
    db: AsyncSession, item: Item, payload: ItemUpdate
) -> Item:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item

async def delete_item(db: AsyncSession, item: Item) -> None:
    await db.delete(item)
    await db.commit()
```

## Step 4: Create the Router

Create `app/api/v1/endpoints/<resource>.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.database import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services import item_service

router = APIRouter()

@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate, db: AsyncSession = Depends(get_db)
) -> ItemRead:
    return await item_service.create_item(db, payload)

@router.get("/", response_model=list[ItemRead])
async def list_items(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[ItemRead]:
    return await item_service.list_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: int, db: AsyncSession = Depends(get_db)
) -> ItemRead:
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int, payload: ItemUpdate, db: AsyncSession = Depends(get_db)
) -> ItemRead:
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return await item_service.update_item(db, item, payload)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_item(
    item_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await item_service.delete_item(db, item)
```

## Step 5: Register the Router

In `app/api/v1/router.py`, add:

```python
from app.api.v1.endpoints import items

api_router.include_router(items.router, prefix="/items", tags=["items"])
```

## Step 6: Create a Migration

```bash
alembic revision --autogenerate -m "add items table"
alembic upgrade head
```

## Checklist

- [ ] Pydantic schemas in `app/schemas/`
- [ ] ORM model in `app/models/`
- [ ] Service functions in `app/services/`
- [ ] Router in `app/api/v1/endpoints/`
- [ ] Router registered in `app/api/v1/router.py`
- [ ] Migration created and applied
- [ ] Tests added in `tests/`
