import os
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, update
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_NAME = 'applications.db'
DATA_DIR = 'data'
DATABASE_URL = f'sqlite+aiosqlite:///{os.path.join(DATA_DIR, DATABASE_NAME)}'

os.makedirs(DATA_DIR, exist_ok=True)
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()


class Applications(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    answered = Column(Boolean, default=False)

    def __repr__(self):
        return f'<User(id={self.id}), name={self.name}'


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def toggle_request_status(request_id: int, status: bool):
    '''Изменяет статус "отвечено" на заданное значение'''
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Applications)
            .where(Applications.id == request_id)
            .values(answered=status)
        )
        await db.commit()


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db():
    '''Получение сессии БД'''
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(create_tables())
    print('Таблица успешно создана!')
