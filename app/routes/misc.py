from fastapi import APIRouter, Depends
from core.database import get_db
from app.models import Category, Currency
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import CategoryResponse, CurrencyResponse

router = APIRouter()

@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = db.execute(select(Category))
    categories = result.scalars().all()
    return categories


@router.get("/currencies/", response_model=List[CurrencyResponse])
async def get_currencies(db: AsyncSession = Depends(get_db)):
    result = db.execute(select(Currency))
    currencies = result.scalars().all()
    return currencies


