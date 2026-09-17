from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from . import models, schemas
from datetime import datetime


def create_advertisement(db: Session, data: schemas.AdvertisementCreate):
    ad = models.Advertisement(
        title=data.title,
        description=data.description,
        price=data.price,
        author=data.author
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def get_advertisement(db: Session, ad_id: int):
    return db.query(models.Advertisement).filter(
        models.Advertisement.id == ad_id
    ).first()


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
    """Поиск объявлений по полям"""
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


def update_advertisement(
    db: Session,
    ad_id: int,
    data: schemas.AdvertisementUpdate
):
    """PATCH — обновление только переданных полей"""
    ad = get_advertisement(db, ad_id)
    if not ad:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
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