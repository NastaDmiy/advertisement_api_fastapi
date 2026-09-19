from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    group = Column(String(20), nullable=False, default='user')  # 'user' или 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String(100), nullable=False)   # имя автора (для отображения)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # владелец
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'author': self.author,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat()
        }