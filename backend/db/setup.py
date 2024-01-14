from db.base import Base
from db.engine import engine


def setup_db():
    Base.metadata.create_all(bind=engine)
