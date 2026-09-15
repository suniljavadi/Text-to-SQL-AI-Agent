import os
os.environ["DATABASE_URL"] = "sqlite:///./test_textsql.db"
from database.seed_data import seed

def pytest_sessionstart(session): seed()
