import databases
import sqlalchemy
from sqlalchemy import MetaData
from .config import settings

# Database connection
database = databases.Database(settings.database_url)

# SQLAlchemy engine and metadata
engine = sqlalchemy.create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

metadata = MetaData()


async def connect_database():
    """Connect to the database."""
    await database.connect()


async def disconnect_database():
    """Disconnect from the database."""
    await database.disconnect()


def create_tables():
    """Create all tables in the database."""
    metadata.create_all(bind=engine)