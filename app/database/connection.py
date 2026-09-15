from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from app.config import get_settings

_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = get_settings().database_url
        kwargs = {"pool_pre_ping": True}
        if url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        _engine = create_engine(url, **kwargs)
    return _engine

def reset_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None

@contextmanager
def connection():
    with get_engine().begin() as conn:
        yield conn

def database_ready() -> bool:
    try:
        with connection() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
