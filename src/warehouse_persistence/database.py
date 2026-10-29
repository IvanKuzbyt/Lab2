from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


def make_engine(path: str | Path) -> Engine:
    location = str(path)
    if location.startswith("sqlite:///"):
        db_file = location[len("sqlite:///") :]
        if db_file != ":memory:":
            Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        url = location
    elif "://" in location:
        raise ValueError("This repository currently supports SQLite DATABASE_URL only")
    else:
        Path(location).parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{location}"
    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def fk_on(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
