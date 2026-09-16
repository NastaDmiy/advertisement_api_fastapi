from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from . import crud, schemas
from .database import Base, engine, get_db

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Advertisement API",
    description="REST API для сайта объявлений купли/продажи",
    version="1.0.0"
)


@app.post(
    '/advertisement',
    response_model=schemas.AdvertisementResponse,
    status_code=201,
    summary="Создать объявление"
)
def create_advertisement(
    data: schemas.AdvertisementCreate,
    db: Session = Depends(get_db)
):
    return crud.create_advertisement(db, data)


@app.get(
    '/advertisement',
    response_model=List[schemas.AdvertisementResponse],
    summary="Поиск объявлений по полям"
)
def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку (частичное совпадение)"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    db: Session = Depends(get_db)
):
    return crud.get_advertisements(db, title, author, min_price, max_price)


@app.get(
    '/advertisement/{advertisement_id}',
    response_model=schemas.AdvertisementResponse,
    summary="Получить объявление по ID"
)
def get_advertisement(
    advertisement_id: int,
    db: Session = Depends(get_db)
):
    ad = crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.patch(
    '/advertisement/{advertisement_id}',
    response_model=schemas.AdvertisementResponse,
    summary="Редактировать объявление (частичное обновление)"
)
def update_advertisement(
    advertisement_id: int,
    data: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db)
):
    ad = crud.update_advertisement(db, advertisement_id, data)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.delete(
    '/advertisement/{advertisement_id}',
    summary="Удалить объявление"
)
def delete_advertisement(
    advertisement_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_advertisement(db, advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {'message': 'Advertisement deleted successfully'}


@app.get('/', summary="Корневой роут")
def root():
    return {
        'message': 'Advertisement API',
        'docs': '/docs',
        'redoc': '/redoc'
    }