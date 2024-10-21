from __future__ import annotations
from sqlalchemy import Column, ForeignKey, Table, select, insert, func
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
    TIMESTAMP,
    BOOLEAN,
    TEXT,
    DATE
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped
from database.engine import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(), primary_key=True)
    tg_id = Column(VARCHAR(255), nullable=False)


class SetName(Base):
    __tablename__ = 'set_name'

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    user_id = Column(ForeignKey(User.id), nullable=False)

    words: Mapped[Word] = relationship()


class Word(Base):
    __tablename__ = 'word'

    id = Column(INTEGER(), primary_key=True)
    first_word = Column(TEXT(), nullable=False)
    second_word = Column(TEXT(), nullable=False)
    set_id = Column(ForeignKey(SetName.id, ondelete='cascade'), nullable=False)


async def init_models():
    async with engine.begin() as session:
        await session.run_sync(Base.metadata.drop_all)
        # await session.run_sync(metadata.create_all)
        await session.run_sync(Base.metadata.create_all)
        # await session.close()