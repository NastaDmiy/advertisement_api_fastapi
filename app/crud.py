from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from . import models, schemas
from .auth import hash_password


# ---------- Реклама ----------

def create_advertisement(db: Session, data: schemas.AdvertisementCreate, author_id: Optional[int] = None):
    ad = models.Advertisement(
        title=data.title,
        description=data.description,
        price=data.price,
        author=data.author,
        author_id=author_id,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def get_advertisement(db: Session, ad_id: int):
    return db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()


def get_advertisements(
    db: Session,
    title: Optional[str] = None,
    description: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
):
    query = db.query(models.Advertisement)

    if title:
        query = query.filter(models.Advertisement.title.ilike(f'%{title}%'))
    if description:
        query = query.filter(models.Advertisement.description.ilike(f'%{description}%'))
    if author:
        query = query.filter(models.Advertisement.author.ilike(f'%{author}%'))
    if min_price is not None:
        query = query.filter(models.Advertisement.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Advertisement.price <= max_price)
    if created_from is not None:
        query = query.filter(models.Advertisement.created_at >= created_from)
    if created_to is not None:
        query = query.filter(models.Advertisement.created_at <= created_to)

    return query.order_by(models.Advertisement.created_at.desc()).all()


def update_advertisement(db: Session, ad_id: int, data: schemas.AdvertisementUpdate):
    ad = get_advertisement(db, ad_id)
    if not ad:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad


def delete_advertisement(db: Session, ad_id: int):
    ad = get_advertisement(db, ad_id)
    if not ad:
        return False
    db.delete(ad)
    db.commit()
    return True


# ---------- Пользователь ----------

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, data: schemas.UserCreate):
    user = models.User(
        username=data.username,
        password_hash=hash_password(data.password),
        group=data.group,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: schemas.UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if 'password' in update_data:
        user.password_hash = hash_password(update_data.pop('password'))
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True