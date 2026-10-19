from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from collections.abc import Generator


DATABASE_URL = "sqlite:///./restaurant.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass



def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
    




