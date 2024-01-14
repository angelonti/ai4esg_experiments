from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import config

__all__ = ["engine", "SQLALCHEMY_DATABASE_URL", "db"]

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{config.db_user}:{config.db_pass}@"
    f"{config.db_host}:{config.db_port}/{config.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DB:
    def __init__(self):
        self.session = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()


db = DB()
