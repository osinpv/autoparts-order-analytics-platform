from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict[str, str]:
    with engine.connect() as connection:
        result = connection.execute(text("select current_database(), current_user"))
        row = result.fetchone()
        return {
            "current_database": row[0],
            "current_user": row[1],
        }