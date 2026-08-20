import sys
from pathlib import Path
import pytest_asyncio

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.database.connection import init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    """Fixture ensuring database tables exist before any test runs."""
    await init_db()
