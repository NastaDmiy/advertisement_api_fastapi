from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from fastapi.security import HTTPBearer

from . import crud, schemas, models
from .database import Base, engine, get_db
from .auth import (
    verify_password, create_access_token,
    get_current_user_optional, get_current_user, require_admin,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Advertisement API",
    description="REST API для сайта объявлений купли/продажи",
    version="2.0.0"
)
security = HTTPBearer(auto_error=False)

# ========== AUTH ==========

@app.post('/login', response_model=schemas.TokenResponse, tags=['auth'])
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid username or password')

    token, expires_in = create_access_token(user.id, user.username, user.group)
    return schemas.TokenResponse(access_token=token, expires_in=expires_in)


# ========== ПОЛЬЗОВАТЕЛЬ ==========

@app.post('/user', response_model=schemas.UserResponse, status_code=201, tags=['user'])
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создание пользователя. Доступно без авторизации."""
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail='Username already exists')
    return crud.create_user(db, data)


@app.get('/user', response_model=List[schemas.UserResponse], tags=['user'])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Список всех пользователей. Только для admin."""
    return db.query(models.User).all()


@app.get('/user/{user_id}', response_model=schemas.UserResponse, tags=['user'])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получение пользователя по id. Доступно без авторизации."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.patch('/user/{user_id}', response_model=schemas.UserResponse, tags=['user'])
def update_user(
    user_id: int,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Обновление пользователя.
    - user может обновлять только себя
    - admin — любого
    """
    if current_user.group != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Forbidden')

    # Только admin может менять группу
    if data.group is not None and current_user.group != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can change group')

    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.delete('/user/{user_id}', tags=['user'])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Удаление пользователя.
    - user может удалить только себя
    - admin — любого
    """
    if current_user.group != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Forbidden')

    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail='User not found')
    return {'message': 'User deleted successfully'}


# ========== РЕКЛАМА ==========

@app.post('/advertisement', response_model=schemas.AdvertisementResponse, status_code=201, tags=['advertisement'])
def create_advertisement(
    data: schemas.AdvertisementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Создание объявления. Только для авторизованных."""
    return crud.create_advertisement(db, data, author_id=current_user.id)


@app.get('/advertisement', response_model=List[schemas.AdvertisementResponse], tags=['advertisement'])
def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку"),
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    created_from: Optional[datetime] = Query(None),
    created_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """Поиск объявлений. Доступно без авторизации."""
    return crud.get_advertisements(
        db, title, description, author,
        min_price, max_price, created_from, created_to,
    )


@app.get('/advertisement/{advertisement_id}', response_model=schemas.AdvertisementResponse, tags=['advertisement'])
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """Получение по id. Доступно без авторизации."""
    ad = crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Advertisement not found')
    return ad


@app.patch('/advertisement/{advertisement_id}', response_model=schemas.AdvertisementResponse, tags=['advertisement'])
def update_advertisement(
    advertisement_id: int,
    data: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Обновление объявления.
    - user — только своё
    - admin — любое
    """
    ad = crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Advertisement not found')

    if current_user.group != 'admin' and ad.author_id != current_user.id:
        raise HTTPException(status_code=403, detail='Forbidden')

    return crud.update_advertisement(db, advertisement_id, data)


@app.delete('/advertisement/{advertisement_id}', tags=['advertisement'])
def delete_advertisement(
    advertisement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Удаление объявления.
    - user — только своё
    - admin — любое
    """
    ad = crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Advertisement not found')

    if current_user.group != 'admin' and ad.author_id != current_user.id:
        raise HTTPException(status_code=403, detail='Forbidden')

    crud.delete_advertisement(db, advertisement_id)
    return {'message': 'Advertisement deleted successfully'}


@app.get('/', tags=['root'])
def root():
    return {
        'message': 'Advertisement API v2.0',
        'docs': '/docs',
        'redoc': '/redoc',
    }