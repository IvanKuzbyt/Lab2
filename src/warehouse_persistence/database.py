from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

def make_engine(path: str | Path):
    engine = create_engine(f"sqlite:///{Path(path)}")
    @event.listens_for(engine, "connect")
    def fk_on(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
    return engine

def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
